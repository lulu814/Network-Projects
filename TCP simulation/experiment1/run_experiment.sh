#!/bin/bash

tcp_variants=("TCP" "TCP/Reno" "TCP/Newreno" "TCP/Vegas")
names=("tcp" "reno" "newreno" "vegas")
duration=20
rm -f result.csv
echo "tcp,cbr rate,throughput,drop_rate,latency">> result.csv
for k in {0..3}
do
    tcp="${tcp_variants[$k]}"
    for i in {1..10}
    do
        rate="${i}mb"
        echo run experiment:"$tcp" "$rate" "$duration"
        for j in {1..10}
        do
            out="out_${names[$k]}_${rate}_${j}.tr"
            ns experiment1.tcl "$tcp" "$rate" "$out" $RANDOM "$duration"
            res=$(python ../tracefile_parser.py "$out" 0 3 "$duration")
            res="${tcp},${rate},${res}"
            echo "$res" >> result.csv
            rm "$out"
        done
    done
done
