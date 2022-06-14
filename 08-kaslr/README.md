# KASLR Break

The code in this folder implements a timer-free KASLR break.

## Preliminaries

- Build the scripts with `make`.
- Make sure you are using the default system configuration with Turbo Boost enabled (`../scripts/set-variable-pstate.sh`).

## How to run

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
Then, these steps were used to run the experiment on an 8-core i7-9700 processor (where 2 cores ran stress):

1. Open two shells.
2. On the first shell, run a 2-core background workload with `taskset -c 0-1 stress-ng --matrix 2 -t 1y`.
3. On the second shell, run the 6-core attack with `./run-kaslr.sh` (see the FIXME in the script to change this for other setups).
4. Run `sudo grep _text /proc/kallsyms | head -1` to get the first address of the ground truth.
5. Run `python parse.py --freq data/out-${date}` with the right `${date}`.
6. To print the means reported in the paper, write down the "mapped" addresses that have a lower frequency into the `ground-truth` array of `parse.py` and re-run. You can also get this ground truth by running a timing based KALSR break.
7. Reboot and repeat with a different randomization as many times as you'd like.