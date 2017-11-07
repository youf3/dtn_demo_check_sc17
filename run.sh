#!/bin/bash

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
cd $bin;
from=$(date +%s)
now=$(date +%y%m%d_%H%M%S)

/usr/bin/python3 ./dtn_demo_check_sc17.py

now=$(date +%s)
total_time=$(expr $now - $from )

echo "$now | $total_time : /bin/python3 ./dtn_demo_check_sc17.py " > run.log
