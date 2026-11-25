#!/bin/bash
# runsym.sh n : a(n) by sym: raise k from 10 until NONE; writes runs/sym_<n>.txt (all sym lines, last FOUND = a(n)).
HERE=$(dirname "$0"); OUT=$HERE/../runs/sym_$1.txt
[ -s $OUT ] && exit 0
k=10; : > $OUT.tmp
while :; do r=$($HERE/sym $1 $k); echo "$r" >> $OUT.tmp; echo "$r" | grep -q NONE && break; k=$((k+1)); done
mv $OUT.tmp $OUT
