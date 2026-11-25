A=(15 16 16 16 16 17 16 16 16 16 16 17 16 17 16 17 17 17 16 17 17)
for i in $(seq 0 20); do n=$((80+i)); [ -s res/$n.txt ] || { ./s $n $((A[i]+1)) > res/$n.txt 2>/dev/null; }; done
