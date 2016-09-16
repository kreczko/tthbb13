#!/bin/bash
WD=`pwd`
for i in `seq 1 200`; do
    qsub -N rq_worker -wd $WD -o $WD/logs/ -e $WD/logs/ worker.sh
done
