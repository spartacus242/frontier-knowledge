#!/bin/bash
# resumable: one segment of width 1.6e9 at a time, sequential (one core)
cd /tmp/work/sq1
W=1600000000
for i in $(seq 0 19); do
  L=$((i*W)); H=$(((i+1)*W))
  f=seg_$i.out
  if [ -f $f ] && grep -q DONE $f; then continue; fi
  s=$(date +%s)
  ./cub $L $H ckpt.csv $f.tmp 2>>run.log && mv $f.tmp $f
  echo "seg $i done in $(( $(date +%s)-s )) s" >> run.log
done
echo ALLDONE >> run.log
