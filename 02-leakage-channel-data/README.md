# Leakage channel - distinguishing data

We used these scripts to test if the scaling of P-states leaks information about the data being processed (Figure 2 in the paper).

## Preliminaries

- Build the scripts with `make`.
- Make sure you are using the default system configuration with Turbo Boost enabled (`../scripts/set-variable-pstate.sh`).

## Collect traces

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
To collect data for Figure 2a, run:
```sh
./run-steady.sh
```

To collect data for Figure 2b, run:
```sh
./run-drops.sh
```

Depending on your machine, you might have to change `samples` and run some background workload (as described in folder `01`), before getting results like Figure 2.
The results are stored in folders named `data/out-steady-${date}` and `data/out-drops-${date}` where `${date}` is a timestamp.

## Plot traces

To plot the traces collected above, run the following (with the correct `${date}`):

For the plot of Figure 2a:
```sh
python ./plot.py --steady data/out-steady-${date}
```

For the plot of Figure 2b:
```sh
python ./plot.py --drops data/out-drops-${date}
```

The script should produce figures similar to Figure 2 in the paper, and store them in the `plot` subfolder.
If you want to plot the raw traces too (for debugging), you can pass the `--raw` flag to the `plot.py` script.
