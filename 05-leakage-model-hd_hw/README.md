# Leakage model - Hamming distance / weight additivity

We used these scripts to test the additivity of HD and HW (Figure 8 in the paper).

## Preliminaries

- Build the scripts with `make`.

## Collect traces

Use the scripts in the `../scripts` folder.

## Plot traces

To plot the traces collected above, depending on the setup you chose, run any of the following (with the correct `${date}`).

For Figure 8a:
```sh
python ../scripts/parse.py --freq data/out-${date}
python ./plot-hd-hw.py --freq data/out-${date} hd-hw-freq
```

For Figures 8b:
```sh
python ../scripts/parse.py --energy data/out-${date}
python ./plot-hd-hw.py --energy data/out-${date} hd-hw-power
```

The scripts should produce figures similar to the ones in the paper, and store them in the `plot` subfolder.
If you want to plot the raw traces too (for debugging), you can pass the `--raw` flag to the `parse.py` script.
