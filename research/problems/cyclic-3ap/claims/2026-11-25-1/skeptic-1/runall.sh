#!/bin/bash
# resumable: one result file per n
cd /tmp/work/sr1
for n in $(seq 3 100); do
  [ -s res/$n.txt ] && continue
  ./rd $n res/$n.tmp 2>/dev/null && mv res/$n.tmp res/$n.txt
done
echo ALLDONE > res/done.flag
