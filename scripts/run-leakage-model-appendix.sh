#!/usr/bin/env bash

TOTAL_PHYSICAL_CORES=`grep '^core id' /proc/cpuinfo | sort -u | wc -l`
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`

# Load MSR module
sudo modprobe msr

# Setup
samples=10000	# 10 seconds
outer=30
num_thread=$TOTAL_LOGICAL_CORES
date=`date +"%m%d-%H%M"`

# Alert
echo "This script will take about $((((10)*$outer*(16+56+48+32+16+56+48+32+16+16)/60+10)/60)) hours. Reduce 'outer' if you want a shorter run."

### Warm Up ###
stress-ng -q --cpu $TOTAL_LOGICAL_CORES -t 10m

### Hamming Distance Input ###
cd ../03-leakage-model-hd
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in `seq 0 16`; do
	echo $selector >> input.txt
done

sudo ./bin/driver-input ${num_thread} ${samples} ${outer}
cp -r out data/out-input-${date}
cd ../scripts

### Hamming Weight Shifts ###
cd ../04-leakage-model-hw
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

# Shift 1
for hamming in {8,16,32,48}; do
	for shift in `seq 0 $((64-$hamming))`; do
		echo $hamming $hamming $shift $shift >> input.txt
	done
done

# Shift 0
for hamming in {8,16,32,48}; do
	for shift in `seq 1 $((64-$hamming))`; do
		echo $hamming $hamming -$shift -$shift >> input.txt
	done
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-shift-${date}
cd ../scripts

### Hamming Weight At Rest ###
cd ../04-leakage-model-hw
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in `seq 0 4 64`; do
	echo $selector >> input.txt
done

sudo ./bin/driver-rest ${num_thread} ${samples} ${outer}
cp -r out data/out-rest-${date}
cd ../scripts

# Unload MSR module
sudo modprobe -r msr
