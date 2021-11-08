#!/usr/bin/env python3

# Compare rankings or sets of rankings.

# Copyright 2021, National Research Council Canada

import sys
import os
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description="Compare rankings.")

parser.add_argument("-s", "--suffixes", type=str, nargs=2, required=True,
                    help="Suffixes of the two experiment types to compare.")
parser.add_argument("-d", "--directory", type=str, help="Directory of ranking files.",
                    default=os.path.join(os.path.dirname(__file__), "..", "rankings"))
parser.add_argument("-l", "--list_of_pairs", type=str, help="List of language pairs to examine.",
                    default=os.path.join(os.path.dirname(__file__),"pairs.txt"))
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output.", default=False)

args = parser.parse_args()


def load_ranking(fn):
    """
    Load a ranking from a file.

    Rankings are formatted as a list of lists representing clusters.

    Argument:
    fn -- path to ranking file
    """
    ranking = []
    cluster = []
    with open(fn) as f:
        for l in f.readlines()[2:]:
            if l.startswith("---------"):
                ranking.append(cluster)
                cluster = []
            else:
                cluster.append(l.strip().split()[2])
    ranking.append(cluster)
    return ranking

def main(args):
    """
    Generate data for table comparing rankings.
    """
    suffix1, suffix2 = args.suffixes
    
    with open(args.list_of_pairs) as f:
        cluster = defaultdict(int)
        rank = defaultdict(int)
        both = defaultdict(int)
        total = defaultdict(int)
        for l in f:
            vers, pair, year, interface = l.strip().split(",")
            pref = os.path.join(args.directory, vers, pair+"-"+year)
            if os.path.isfile(pref+"."+suffix1) and os.path.isfile(pref+"."+suffix2):
                f1 = pref+"."+suffix1
                f2 = pref+"."+suffix2
                
                r1, r2 = load_ranking(f1), load_ranking(f2)
                
                # Determine if the ranking is identical:
                identical = r1 == r2
                
                # Check if there are the same clusters, in the same order
                # Ranks within clusters may differ
                same_clusters = [sorted(sublist) for sublist in r1] \
                                == [sorted(sublist) for sublist in r2]

                # Check if systems are in the same order, regardless of cluster
                same_rank = [item for sublist in r1 for item in sublist] \
                            == [item for sublist in r2 for item in sublist]
                
                # Confirm that the same systems are listed the same number of times
                # Note: all experiments in paper compare rankings with identical sets of systems.
                same_systems = sorted([item for sublist in r1 for item in sublist]) \
                               == sorted([item for sublist in r2 for item in sublist])

                if args.verbose:
                    print("\t".join([str(x) for x in
                                     [same_systems, same_rank, same_clusters, identical, f1, f2]]))

                # Increment according to whether each type of change occurs
                total[(vers,year,interface)] += 1
                rank[(vers,year,interface)] += (0 if same_rank else 1)
                cluster[(vers,year,interface)] += (0 if same_clusters else 1)
                both[(vers,year,interface)] += (0 if same_rank or same_clusters else 1)
                
            else:
                for suffix in [suffix1, suffix2]:
                    if not os.path.isfile(pref+"."+suffix):
                        print("\t".join(["Ranking unavailable:",l.strip(),suffix]),
                              file=sys.stderr)

    # Collect SR-DC and SR+DC totals
    for dct in [total, rank, cluster, both]:
        for vers in ["SR-DC", "SR+DC"]:
            dct[(vers, "all", "all")] = sum([dct[x] for x in dct if x[0] == vers])

    # Table rows to output
    rows = [("SR-DC", "2018", "2018"), ("SR-DC", "2019", "mturk"),
            ("SR-DC", "2020", "mturk"), ("SR-DC", "all", "all"),
            ("SR+DC", "2019", "mturk"), ("SR+DC", "2019", "appraise"),
            ("SR+DC", "2020", "mturk"), ("SR+DC", "2020", "appraise"),
            ("SR+DC", "all", "all")]

    # Output information from tables in paper
    print("Vers/Year/Interface", "Rank", "Cluster", "Both")
    for row in rows:
        r, c, b, t = [str(x) for x in [rank[row], cluster[row], both[row], total[row]]]
        print(",".join(row), "/".join([r,t]), "/".join([c,t]), "/".join([b,t]))

if __name__ == "__main__":
    main(args)
