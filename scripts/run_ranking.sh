#!/bin/bash

# Generate rankings required to replicate tables from paper.
# This script is called by scripts/run_all_rankings.sh

# Copyright 2021, National Research Council Canada

if [ $# -ne 6 ]; then
    echo "USAGE: $0 input src trg rankings_dir version year " >&2
    exit
fi

s_dir="$(dirname $(realpath $0))" # Scripts directory

inp=$1 # Input file
src=$2 # Source language
trg=$3 # Target language
r_dir=$4 # Ranking (output) directory
v=$5 # SR-DC or SR+DC
y=$6 # 2018, 2019 or 2020

pref=$r_dir/$v/$src-$trg-$y # Output prefix

# Generate original rankings (compare to Findings papers; Table 4)
$s_dir/get_ranking.py -i $inp -s $src -t $trg > $pref.orig

# Generate rankings without ref/human systems (Table 2)
$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_human > $pref.rh
$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_human_sig > $pref.orig-rhs

# Generate rankings with lowest/highest-scoring system removed (Table 3)
$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_lowest $pref.orig > $pref.rlow
$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_lowest_sig $pref.orig > $pref.orig-rlows

$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_highest $pref.orig > $pref.rhigh
$s_dir/get_ranking.py -i $inp -s $src -t $trg --remove_highest_sig $pref.orig > $pref.orig-rhighs

# Generate rankings with degraded ref/human systems scores (Fig. 1)
for d in 1.25 1.5 2 4 10; do 
    $s_dir/get_ranking.py -i $inp -s $src -t $trg -d $d --remove_human_sig > $pref.d-$d-rhs
done
