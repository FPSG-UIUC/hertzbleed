# Leakage model - Hamming distance

We used these scripts to test the HD leakage model (Figures 4, 14 in the paper).

## Preliminaries

- Build the scripts with `make`.

## Collect traces

Use the scripts in the `../scripts` folder.

## Plot traces

To plot the traces collected above, depending on the setup you chose, run either one of the following (with the correct `${date}`).

For the frequency plot (Figure 4a or 14a):
```sh
python ../scripts/parse.py --freq data/out-${date}
python ./plot-hd.py --freq data/out-${date} hd-freq
```

For the power consumption plot (Figure 4b or 14b):
```sh
python ../scripts/parse.py --energy data/out-${date}
python ./plot-hd.py --energy data/out-${date} hd-power
```

The scripts should produce figures similar to the ones in the paper, and store them in the `plot` subfolder.
If you want to plot the raw traces too (for debugging), you can pass the `--raw` flag to the `parse.py` script.
