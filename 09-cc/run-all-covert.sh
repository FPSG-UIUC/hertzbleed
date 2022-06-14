#!/bin/bash

# Parse args
if [ $# -eq 1 ]; then
	INTERVAL=$1
elif [ $# -lt 1 ]; then
	INTERVAL=100000000
else
	echo "ERROR: Incorrect number of arguments"
	echo "./run.sh [interval]"
	exit
fi

# Run sending threads on all but 1 core
TOTAL_LOGICAL_CORES=`grep '^core id' /proc/cpuinfo | wc -l`
NTASKS=$(($TOTAL_LOGICAL_CORES-1))

echo "Running covert channel test with an interval of $INTERVAL cycles and $NTASKS sending threads"

# Kill previous processes
sudo killall sender &> /dev/null

# Run
until
	# Start sender
	sudo ./bin/sender $INTERVAL $NTASKS > /dev/null &

	# Warm up gap
	sleep 60

	# Start receiver
	sudo ./bin/receiver $INTERVAL > /dev/null
do
	echo "Repeating iteration $i because it failed"
	sudo killall sender &> /dev/null
done

sleep 0.05
sudo killall sender &> /dev/null
