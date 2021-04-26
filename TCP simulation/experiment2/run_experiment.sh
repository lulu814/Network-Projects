#!/bin/bash

tcp_variants=("Reno Reno" "Newreno Reno" "Vegas Vegas" "Newreno Vegas")
names=("reno_reno" "newreno_reno" "vegas_vegas" "newreno_vegas")
duration=100
rm -f result.csv
echo "tcp,cbr rate,t1_throughput,t1_drop_rate,t1_latency,t2_throughput,t2_drop_rate,t2_latency">> result.csv
for k in {0..3}
do
    tcp_pair="${tcp_variants[$k]}"
    for i in {1..10}
    do
        rate="${i}mb"
        echo run experiment:"$tcp_pair" "$rate" "$duration"
        for j in {1..10}
        do
            out="out_${names[$k]}_${rate}_${j}.tr"
            ns experiment2.tcl $tcp_pair "$rate" "$out" $RANDOM "$duration"
            res1=$(python ../tracefile_parser.py "$out" 0 3 "$duration")
            res2=$(python ../tracefile_parser.py "$out" 4 5 "$duration")
            res="${tcp_pair},${rate},${res1},${res2}"
            echo "$res" >> result.csv
            rm "$out"
        done
    done
done
