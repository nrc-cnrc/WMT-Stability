#!/bin/bash

# Generate all rankings from the paper.

# Copyright 2021, National Research Council Canada

# For efficiency, you may wish to run them in parallel.
# Edit this to submit jobs to scheduler
# e.g.: run_command="qsub"
# As written, jobs will run sequentially and may take quite some time to complete
run_command=""

data_dir="$(dirname $(dirname $(realpath $0)) )/data"
scripts_dir="$(dirname $(realpath $0))"

# Ranking directory setup:
for v in SR-DC SR+DC; do
    rankings_dir="$(dirname $(dirname $(realpath $0)) )/rankings"
    mkdir -p $rankings_dir/$v
done

# en-* 2018 SR-DC
for trg in cs de et fi ru tr zh; do
    src=en
    y=2018
    v=SR-DC
    echo "$src-$trg $y"
    inputfile=$data_dir/newstest2018-humaneval/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# *-en 2018 SR-DC
for src in cs de et fi ru zh; do
    trg=en
    y=2018
    v=SR-DC
    echo "${src}-$trg $y"
    inputfile=$data_dir/newstest2018-humaneval/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# en-* 2019 SR+DC (Appraise)
for trg in cs de fi gu kk lt ru zh; do
    src=en
    y=2019
    v=SR+DC
    echo "$src-$trg $y"
    inputfile=$data_dir/newstest2019-humaneval/appraise-doclevel-humaneval-newstest2019/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# *-en 2019 SR-DC (MTurk)
for src in fi gu kk lt ru; do
    trg=en
    y=2019
    v=SR-DC
    echo "${src}-$trg $y"
    inputfile=$data_dir/newstest2019-humaneval/mturk-sntlevel-humaneval-newstest2019/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# {de,zh}-en 2019 SR+DC (MTurk)
for src in de zh; do
    trg=en
    y=2019
    v=SR+DC
    inputfile=$data_dir/newstest2019-humaneval/mturk-doclevel-humaneval-newstest2019/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# en-* 2020 SR+DC (Appraise)
for trg in zh cs de iu ja pl ru ta; do
    src=en
    y=2020
    v=SR+DC
    echo "$src-${trg} $y"
    inputfile=$data_dir/newstest2020-humaneval/appraise-doclevel-humaneval-newstest2020
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# *-en 2020 SR+DC (MTurk)
for src in cs de ja pl ru ta zh; do
    trg=en
    y=2020
    v=SR+DC
    echo "${src}-$trg $y"
    inputfile=$data_dir/newstest2020-humaneval/mturk-doclevel-humaneval-newstest2020
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

# {iu,km,ps}-en 2020 SR-DC (MTurk)
for src in iu km ps; do
    trg=en
    y=2020
    v=SR-DC
    echo "${src}-$trg $y"
    inputfile=$data_dir/newstest2020-humaneval/mturk-sntlevel-humaneval-newstest2020/analysis
    $run_command $scripts_dir/run_ranking.sh $inputfile $src $trg $rankings_dir $v $y
done

