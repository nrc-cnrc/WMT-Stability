#!/bin/bash

# Download and extract the human annotation data.

# Copyright 2021, National Research Council Canada

data_dir="$(dirname $(dirname $(realpath $0)) )/data"

mkdir -p $data_dir

cd $data_dir

wget https://www.scss.tcd.ie/~ygraham/newstest2020-humaneval.tar.gz
wget https://www.computing.dcu.ie/~ygraham/newstest2019-humaneval.tar.gz
wget https://www.computing.dcu.ie/~ygraham/newstest2018-humaneval.tar.gz

tar -zxvf newstest2020-humaneval.tar.gz
tar -zxvf newstest2019-humaneval.tar.gz
tar -zxvf newstest2018-humaneval.tar.gz
