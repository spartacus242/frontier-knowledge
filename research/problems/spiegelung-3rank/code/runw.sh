#!/bin/bash
# runw.sh X W dir : all windows for positive D to X and negative D to 3X; skips finished windows (resumable).
X=$1; W=$2; DIR=$3; HERE=$(dirname "$0"); mkdir -p $DIR
for sg in p n; do
  if [ $sg = p ]; then TOP=$X; S=1; else TOP=$((3*X)); S=-1; fi
  i=0
  while [ $((i*W)) -lt $TOP ]; do
    lo=$((i*W)); hi=$(((i+1)*W)); [ $hi -gt $TOP ] && hi=$TOP
    [ -f $DIR/${sg}_$i.bin ] || $HERE/cubicw $S $lo $hi $DIR/${sg}_$i.bin >> $DIR/log.txt || exit 1
    i=$((i+1))
  done
done
echo ALLDONE >> $DIR/log.txt
