#!/usr/bin/env bash

TOTAL_PHYSICAL_CORES=`grep '^core id' /proc/cpuinfo | sort -u | wc -l`
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`

# Load MSR module
sudo modprobe msr

# Setup
samples=40000		# 40 seconds
outer=105			# 105 reps
num_thread=$TOTAL_LOGICAL_CORES
date=`date +"%m%d-%H%M"`

# Alert
echo "This script will take about $(((30+40)*$outer*3/60/60)) hours. Reduce 'outer' if you want a shorter run."

# Run
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in 16 32 48; do
	echo $selector >> input.txt
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-drops-${date}

# Unload MSR module
sudo modprobe -r msr