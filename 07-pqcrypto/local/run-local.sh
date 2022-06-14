#!/usr/bin/env bash

TOTAL_PHYSICAL_CORES=`grep '^core id' /proc/cpuinfo | sort -u | wc -l`
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`

# Load MSR module
sudo modprobe msr

# Setup
samples=200000	# 200 seconds
outer=4
date=`date +"%m%d-%H%M"`

# Prepare
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

# Write selectors
echo 0 1 2 300 >> input.txt
echo 1 1 2 300 >> input.txt
echo 0 2 5 300 >> input.txt
echo 1 2 5 300 >> input.txt
echo 0 3 9 300 >> input.txt
echo 1 3 9 300 >> input.txt
echo 0 4 13 300 >> input.txt
echo 1 4 13 300 >> input.txt
echo 0 5 15 300 >> input.txt
echo 1 5 15 300 >> input.txt
echo 0 6 45 300 >> input.txt
echo 1 6 45 300 >> input.txt
echo 0 7 234 300 >> input.txt
echo 1 7 234 300 >> input.txt
echo 0 8 275 300 >> input.txt
echo 1 8 275 300 >> input.txt
echo 0 9 150 300 >> input.txt
echo 1 9 150 300 >> input.txt
echo 0 10 170 300 >> input.txt
echo 1 10 170 300 >> input.txt
echo 0 1 150 300 >> input.txt
echo 1 1 150 300 >> input.txt
echo 0 2 50 300 >> input.txt
echo 1 2 50 300 >> input.txt
echo 0 3 70 300 >> input.txt
echo 1 3 70 300 >> input.txt
echo 0 4 80 300 >> input.txt
echo 1 4 80 300 >> input.txt
echo 0 5 90 300 >> input.txt
echo 1 5 90 300 >> input.txt
echo 0 6 100 300 >> input.txt
echo 1 6 100 300 >> input.txt
echo 0 7 150 300 >> input.txt
echo 1 7 150 300 >> input.txt
echo 0 8 180 300 >> input.txt
echo 1 8 180 300 >> input.txt
echo 0 9 190 300 >> input.txt
echo 1 9 190 300 >> input.txt
echo 0 10 270 300 >> input.txt
echo 1 10 270 300 >> input.txt

# Warm Up
stress-ng -q --cpu $TOTAL_LOGICAL_CORES -t 10m

# Run
sudo ./bin/driver ${samples} ${outer}
cp -r out data/out-${date}

# Unload MSR module
sudo modprobe -r msr
