#!/usr/bin/env bash

TOTAL_PHYSICAL_CORES=`grep '^core id' /proc/cpuinfo | sort -u | wc -l`
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`

# Load MSR module
sudo modprobe msr

# Parse args
if [ $# -eq 1 ]; then
	outer=$1
elif [ $# -lt 1 ]; then
	outer=1
else
	echo "ERROR: Incorrect number of arguments"
	echo "./run.sh [outer]"
	exit
fi

# Setup
samples=3500	# 17.5 seconds (one sample every 5 milliseconds)
num_thread=$TOTAL_LOGICAL_CORES
date=`date +"%m%d-%H%M"`

# Alert
echo "This script will take about $(((90+18)*$outer*2/60)) minutes"

# Run
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in int32float int32; do
	echo $selector >> input.txt
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-${date}

# Unload MSR module
sudo modprobe -r msr