#!/bin/bash
# resumable driver: one segment at a time, skip finished ones
cd /tmp/work/sq3
XM1=31622776603
S=4294967296
for i in 0 1 2 3 4 5 6 7; do
  d0=$((i*S)); d1=$(((i+1)*S)); [ $d1 -gt $XM1 ] && d1=$XM1
  out=seg_$i.txt
  [ -s $out ] && continue
  s=$(date +%s)
  ./cub seg $d0 $d1 $out.tmp 2> log_$i.txt && mv $out.tmp $out
  echo "seg $i $d0 $d1 $(( $(date +%s)-s ))s" >> timing.txt
done
echo DONE >> timing.txt
