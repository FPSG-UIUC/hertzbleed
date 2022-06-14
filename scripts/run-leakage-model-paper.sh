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
echo "This script will take about $((((10)*$outer*(16+64+64+255+8+64*4)/60+10)/60)) hours. Reduce 'outer' if you want a shorter run."

### Warm Up ###
stress-ng -q --cpu $TOTAL_LOGICAL_CORES -t 10m

### Hamming Distance ###
cd ../03-leakage-model-hd
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in `seq 0 16`; do
	echo $selector >> input.txt
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-${date}
cd ../scripts

### Hamming Weight ###
cd ../04-leakage-model-hw
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

# HW increasing from right
for hamming in `seq 0 64`; do
	echo $hamming $hamming 0 0 >> input.txt
done

# HW increasing from left
for hamming in `seq 0 64`; do
	echo $hamming $hamming $((64-$hamming)) $((64-$hamming)) >> input.txt
done

# HW effect at each byte granularity
for hamming in `seq 100 355`; do
	echo $hamming 0 0 0 >> input.txt
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-${date}

# HW effect non-consecutive
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for selector in `seq 0 8`; do
	echo $selector >> input.txt
done

sudo ./bin/driver-nc ${num_thread} ${samples} ${outer}
cp -r out data/out-nc-${date}
cd ../scripts

### Hamming Weight + Hamming Distance ###
cd ../05-leakage-model-hd_hw
sudo rm -rf out
mkdir out
sudo rm -rf input.txt

for hamming_first in {16,32}; do
	for hamming_second in `seq 0 64`; do
		echo $hamming_first $hamming_second 0 0 >> input.txt
	done	
done

for hamming_first in {16,32}; do
	for hamming_second in `seq 0 64`; do
		echo $hamming_first $hamming_second $((64-$hamming_first)) 0 >> input.txt
	done
done

sudo ./bin/driver ${num_thread} ${samples} ${outer}
cp -r out data/out-${date}
cd ../scripts

# Unload MSR module
sudo modprobe -r msr