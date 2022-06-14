#!/usr/bin/env bash

TOTAL_PHYSICAL_CORES=`grep '^core id' /proc/cpuinfo | sort -u | wc -l`
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`

# Load MSR module
sudo modprobe msr

# Setup
samples=11	# one every 10 ms
outer=1
date=`date +"%m%d-%H%M"`

# FIXME: change depending on machine
num_thread=6
# num_thread=$TOTAL_LOGICAL_CORES

# Alert
echo "This script will take about $(($samples*$outer*512/100+60)) seconds. Reduce 'outer' if you want a shorter run."

# Clean up
sudo rm -rf out
mkdir out

# Warm Up
stress-ng -q --cpu ${num_thread} -t 1m

# KASLR Test
./bin/driver ${num_thread} ${samples} ${outer}

# Copy results
cp -r out data/out-${date}

# Unload MSR module
sudo modprobe -r msr
