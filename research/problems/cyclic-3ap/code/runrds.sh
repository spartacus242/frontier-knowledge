#!/bin/bash
# runrds.sh lo hi jobs : rds2 for each n in lo..hi, skipping finished ones (runs/rds2_<n>.txt), 'jobs' at a time.
HERE=$(dirname "$0"); OUT=$HERE/../runs
seq $1 $2 | xargs -P $3 -I{} bash -c "[ -s $OUT/rds2_{}.txt ] || { $HERE/rds2 {} > $OUT/rds2_{}.tmp && mv $OUT/rds2_{}.tmp $OUT/rds2_{}.txt; }"
