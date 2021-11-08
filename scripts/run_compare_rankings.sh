#!/bin/bash

# Generate Tables 2 and 3 and values for Fig. 1 from paper

# Copyright 2021, National Research Council Canada

scripts_dir="$(dirname $(realpath $0))"

# Compare rankings for Table 2:
echo "Table 2:"
$scripts_dir/compare_rankings.py -s rh orig-rhs

# Compare rankings for Table 3:
echo ""
echo "Table3:"
$scripts_dir/compare_rankings.py -s rlow orig-rlows | grep "all"
$scripts_dir/compare_rankings.py -s rhigh orig-rhighs | grep "all"

# Compare rankings for Figure 1:
echo ""
echo "Figure 1:"
for divisor in 1.25 1.5 2 4 10; do
    echo "Div.: $divisor"
    $scripts_dir/compare_rankings.py -s d-$divisor-rhs orig-rhs | grep "all"
    echo ""
done
