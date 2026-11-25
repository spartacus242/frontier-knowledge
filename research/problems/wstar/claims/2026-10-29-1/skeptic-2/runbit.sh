#!/bin/bash
cd /tmp/work/skeptic2
start=0; [ -f jobsbit.txt ] && start=$(grep -c '^JOB' jobsbit.txt)
./bit 76 5 12 $start >> jobsbit.txt
