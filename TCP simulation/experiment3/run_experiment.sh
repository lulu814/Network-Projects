#!/bin/bash

queuing_algorithms=("DropTail"  "RED")
tcp_variants=("Reno" "Sack1")
duration=20
rm -f result.csv
echo "tcp,algorithm,tcp_throughput,tcp_latency,cbr_throughput,cbr_latency">> result.csv
for k in {0..1}
do
    tcp="${tcp_variants[$k]}"
    for l in {0..1}
    do
        algorithm="${queuing_algorithms[$l]}"
        echo run experiment:"$algorithm" "$tcp" "$duration"
        for j in {1..100}
        do
            out="out_${tcp}_${algorithm}_${j}.tr"
            ns experiment3.tcl "$tcp" "$algorithm" "$out" $RANDOM 8 "$duration"
            res1=$(python ./parser.py "$out" 0 3 "$duration" tcp)
            res2=$(python ./parser.py "$out" 4 5 "$duration" cbr)
            res="${tcp},${algorithm},${res1},${res2}"
            echo "$res" >> result.csv
            rm "$out"
        done
    done
done
