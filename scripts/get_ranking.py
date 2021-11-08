#!/usr/bin/env python3

# Generate ranking for a language pair.

# Copyright 2021, National Research Council Canada

import sys
import os.path
from collections import defaultdict, namedtuple
from scipy import stats
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Generate ranking for language pair.")

parser.add_argument("-i", "--input", type=str, help="Input directory.", required=True)
parser.add_argument("-s", "--src", type=str, help="Source language.", required=True)
parser.add_argument("-t", "--trg", type=str, help="Target language.", required=True)
parser.add_argument("-d", "--divide", type=float, default=1.0,
                    help="Divide human and/or ref values by divisor.")
parser.add_argument("--remove_human", action="store_true", default=False,
                    help="Remove human/ref system(s) from all calculations.")
parser.add_argument("--remove_human_sig", action="store_true", default=False,
                    help="Remove human system(s) from clusters.")
parser.add_argument("--remove_highest", type=str, default=None,
                    help="Path to original ranking, used to remove highest from all calculations.")
parser.add_argument("--remove_highest_sig", type=str, default=None,
                    help="Path to original ranking, used to remove highest from clusters.")
parser.add_argument("--remove_lowest", type=str, default=None,
                    help="Path to original ranking, used to remove lowest from all calculations.")
parser.add_argument("--remove_lowest_sig", type=str, default=None,
                    help="Path to original ranking, used to remove lowest from clusters.")
parser.add_argument("-r", "--remove", type=str, nargs="+", default=[],
                    help="List of systems to remove from all calculations.")
parser.add_argument("-g", "--sig_remove", type=str, nargs="+", default=[],
                    help="List of systems to remove from clusters.")

args=parser.parse_args()

Score = namedtuple("Score", ["hit", "system", "sid", "score"])

def get_system_name(fn, highest):
    """
    Return the name of the lowest or highest ranked system from a ranking.

    Arguments:
    fn -- path to ranking file
    highest -- True if highest, False for lowest
    """
    with open(fn) as f:
        if highest:
            return f.readlines()[2].strip().split()[-1]
        else:
            return f.readlines()[-1].strip().split()[-1]

def average_duplicates(system_lst, s):
    """
    Return list of scores with all duplicate scores averaged.
    A duplicate score is 2 or more scores for the same sent. ID (sid) and system.

    Arguments:
    system_lst -- list of all scores for system s
    s -- system name
    """
    sids = set([x.sid for x in system_lst])
    deduped = []
    for sid in sids:
        sid_scores = [x for x in system_lst if x.sid == sid]
        hits = ",".join([x.hit for x in sid_scores])
        deduped.append(Score(hits, s, sid,
                             np.mean([x.score for x in sid_scores])))
    return deduped

def keep(system, stype, removed, remove_human):
    """
    Return a boolean for whether a score should be kept.

    Arguments:
    system -- string with name of system
    stype -- score type (e.g. REF)
    removed -- set of systems to be removed
    remove_human -- boolean indicating if human scores should be removed
    """
    if system in removed:
        return False
    elif remove_human and stype=="REF":
        return False
    elif remove_human and "HUMAN" in system:
        return False
    else:
        return True

def keep_sig(system, sig_removed, remove_human_sig):
    """
    Return a boolean for whether a system should be in the final ranking/significance 
    cluster calculations.

    Arguments:
    system -- string with name of system
    sig_removed -- set of systems to remove from significance cluster calcs.
    remove_human_sig -- bool: if removing human scores from sig. cluster calcs.
    """
    if system in sig_removed:
        return False
    elif remove_human_sig and "HUMAN" in system:
        return False
    else:
        return True

def main(args):
    """
    Generate ranking for language pair, with desired modifications.
    """
    
    inputdir = args.input
    srclng = args.src # Source language
    trglng = args.trg # Target language

    removed = set(args.remove) # Set of systems to remove from all calculations
    sig_removed = set(args.sig_remove) # Set to remove from rank/clusters only

    # Add highest/lowest to removal sets if requested.
    if args.remove_highest is not None:
        removed.add(get_system_name(args.remove_highest, True))
    if args.remove_highest_sig is not None:
        sig_removed.add(get_system_name(args.remove_highest_sig, True))
    if args.remove_lowest is not None:
        removed.add(get_system_name(args.remove_lowest, False))
    if args.remove_lowest_sig is not None:
        sig_removed.add(get_system_name(args.remove_lowest_sig, False))

    remove_human = args.remove_human
    remove_human_sig = args.remove_human_sig

    d = args.divide
    divide = False if args.divide == 1.0 else True

    # Extract the raw scores for each worker ID, used to calculate mu and std.
    # This is done from ad-latest.csv.
    # Build a dictionary (hit_scores) mapping from worker ID to list of scores.
    hit_scores = defaultdict(list)
    with open(os.path.join(inputdir,"ad-latest.csv")) as f:
        for l in f:
            hitid,workerid,src,trg,_,_,system,_,stype,sid,score,_ = l.strip().split()
            if src == srclng and trg == trglng and keep(system, stype, removed, remove_human):
                hit = workerid
                if divide:
                    if stype=="REF" or "HUMAN" in system:
                        score = float(score)/d
                hit_scores[hit].append(float(score))

    # Compute mean and standard deviation for each "hit" (worker ID).                
    hit_vals = {}
    for hit in hit_scores:
        hit_vals[hit] = (np.mean(hit_scores[hit]), np.std(hit_scores[hit], ddof=1))

    # Collect the valid (SYSTEM and REPEAT) scores from ad-good-raw-redup.csv
    scores = []
    with open(os.path.join(inputdir, "ad-good-raw-redup.csv")) as f:
        for l in f:
            hitid,workerid,src,trg,_,_,system,_,stype,sid,score,_=l.strip().split()
            if src == srclng and trg == trglng and keep(system, stype, removed, remove_human):
                hit = workerid
                if stype == "SYSTEM" or stype == "REPEAT":
                    if divide:
                        if "HUMAN" in system:
                            score = float(score)/d
                    scores.append(Score(hit, system, sid, float(score)))
                
    # Get the set of "hits" (worker IDs on MTurk, HITs on Appraise)
    hits = set([x.hit for x in scores])

    # Get the set of systems
    systems = set([x.system for x in scores])

    # For each HIT, get the score information (full_hit)
    # And just the raw scores (hit_raw_scores)
    # Compute z-scores using mu and std
    # Collect all z-scores
    zscores = []
    for hit in hits:
        full_hit = [x for x in scores if x.hit == hit]
        hit_raw_scores = [x.score for x in scores if x.hit == hit]
        mu, s = hit_vals[hit]
        if s != 0 and s == s: #This checks for NaN
            hit_z_scores = [(x-mu)/s for x in hit_raw_scores]
            zscores += [Score(full_hit[i].hit, full_hit[i].system,
                              full_hit[i].sid, hit_z_scores[i]) for i in range(len(full_hit))]

    # Remove any systems that should be removed before significance clusters:
    new_system_list = []
    for s in systems:
        if keep_sig(s, sig_removed, remove_human_sig):
            new_system_list.append(s)
    systems = new_system_list

    # Average any scores (raw or z-score) for segments that have been annotated multiple times
    # Compute system averages
    final_scores = []
    sys_scores = defaultdict(list)
    sys_z_scores = defaultdict(list)
    for s in systems:
        sys_scores[s] = average_duplicates([x for x in scores if x.system == s], s)
        sys_z_scores[s] = average_duplicates([x for x in zscores if x.system == s], s)
        final_scores.append((np.mean([x.score for x in sys_z_scores[s]]),
                             np.mean([x.score for x in sys_scores[s]]), s))
    
    #Sort the systems by z-score
    sorted_systems = sorted(final_scores, reverse=True)

    # Produce the ranking table, with significance lines between clusters
    # where all systems below a given system are significantly worse than
    # the given system.
    print("   Ave.   Ave.z  System\n-----------------------------------------")
    for i in range(len(sorted_systems)):
        z,raw,s = sorted_systems[i]
        print("{:>7.1f}".format(raw), "{:>7.3f}".format(z), s)
        n = 1
        max_sig = 0.0
        z_list = [x.score for x in sys_z_scores[s]]
        while i+n < len(sorted_systems) and max_sig < 0.5:
            next_z_list = [x.score for x in sys_z_scores[sorted_systems[i+n][2]]]
            sig = stats.mannwhitneyu(z_list,next_z_list)[1]
            if sig > max_sig:
                max_sig = sig
            n += 1
        if i+1 < len(sorted_systems):
            if max_sig < 0.001:
                print("----------------------------------------TT (0.001)")
            elif max_sig < 0.01:
                print("-----------------------------------------T (0.01)")
            elif max_sig < 0.05:
                print("-----------------------------------------X (0.05)")
                
if __name__ == "__main__":
    main(args)
