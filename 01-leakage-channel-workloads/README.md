# Leakage channel - distinguishing instructions

We used these scripts to test if the scaling of P-states leaks information about the current workload (Figure 1 in the paper).

## Preliminaries

- Build the scripts with `make`.
- Make sure you are using the default system configuration with Turbo Boost enabled (`../scripts/set-variable-pstate.sh`).

## Collect traces

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
Then, to reproduce the results of the paper, run:
```sh
./run.sh
```

The above script collects one trace per workload (stress-ng's `int32` and `int32float`).
You can collect `k > 1` traces per workload by using `./run.sh k` (the default is `k = 1`).
The results are stored in a folder named `data/out-${date}` where `${date}` is a timestamp.

## Plot traces

To plot the traces collected above, run the following (with the correct `${date}`):
```sh
python ./plot.py data/out-${date}
```

The script should produce figures similar to Figure 1 in the paper, and store them in the `plot` subfolder.

## Notes

On machines with particularly good coolers, the results of the above experiment might not look like the ones shown in Figure 1 in the paper.
On these machines, the frequency might take longer to drop below the maximum P-state, or even stay at the maximum P-state forever with the workloads we chose.
In these cases, we suggest to try the following test:

1. Open 2 shells.
2. On the first shell, run this and keep it open so you can see how the frequency changes in real time:
```sh
watch -n 0 "cat /proc/cpuinfo | grep \"^[c]pu MHz\""
```
3. On the second shell, run:
```sh
stress-ng -q --cpu `nproc` -t 10m
```
4. Do you ever see the frequency drop below the initial value?
5. If the frequency eventually drops below the initial value, write down how long it took for the frequency to drop, and adjust the length of a trace by changing the `samples` variable in `run.sh` accordingly.
6. If the frequency never drops below the initial value, stop `stress-ng` and run it again with a heavier workload as follows:
```sh
stress-ng -q --matrix `nproc` -t 10m
```
7. Do you ever see the frequency drop below the initial value?
8. If the frequency never drops below the initial value, your machine's cooler is so good that it's unlikely that the frequency will drop to steady state during an attack. 
Try a different machine.
9.  If the frequency eventually drops below the initial value, then you need this heavier workload running in the background on at least some cores during the actual experiment.
10.   Pick `k` cores (with `k > 1`, and starting from `k = 1`) to run this background workload. 
For example, if you pick the two cores 0 and 1, run the following command (make sure to adjust `-c 0-1` to the CPU IDs you picked, and `--matrix 2` to `--matrix k`):
```sh
taskset -c 0-1 stress-ng --matrix 2 -t 1y
```
11.  Change the `num_thread` variable in `run.sh` to be the number of logical cores minus `k`.
12.  Repeat the experiment until you see the frequency drop in the figures.