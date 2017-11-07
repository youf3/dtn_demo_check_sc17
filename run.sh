#!/bin/bash

bin=`dirname "$0"`
bin=`cd "$bin"; pwd`
cd $bin;
from=$(date +%s)
starttime=$(date +%y%m%d_%H%M%S)

/usr/bin/python3 ./dtn_demo_check_sc17.py > ./.tmp.data

now=$(date +%s)
total_time=$(expr $now - $from )

echo "$starttime | $total_time : "$(cat ./.tmp.data) >> run.log
