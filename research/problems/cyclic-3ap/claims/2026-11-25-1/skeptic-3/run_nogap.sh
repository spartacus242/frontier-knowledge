#!/bin/bash
# resumable: one result file per n; skip if done
cd /tmp/work/sr3
for n in $(seq 80 100); do
  a=$(awk -F, -v n=$n '$1==n{print $2}' /tmp/work/pk3/terms.csv)
  f=res_nogap/$n.txt
  [ -s $f ] && grep -q DONE $f && continue
  s=$(date +%s.%N); lo=$(./cyc_nogap $n $a); m=$(date +%s.%N)
  hi=$(./cyc_nogap $n $((a+1))); e=$(date +%s.%N)
  echo "$lo  time=$(echo "$m-$s"|bc)" > $f.tmp
  echo "$hi  time=$(echo "$e-$m"|bc)" >> $f.tmp
  echo DONE >> $f.tmp; mv $f.tmp $f
done
