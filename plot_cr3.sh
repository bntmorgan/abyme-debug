#!/bin/bash
od -t x8 -w8 cr3 | cut -d " " -f 2  | cat -n > data

(
cat << ddd
set terminal png size 1200,800
#set yrange [0:30000000000]
#set xrange [300000:]
set logscale y
set format y "%x"; 
plot "data" using 1:2 index 0 title "cr3"
ddd
) | gnuplot > file.png
feh file.png
