# Covert channel

The code in this folder implements a timer-free covert channel.
The `sender` transmits a sequence of zeros and ones.
The `receiver` collects a number of frequency samples.
Then these samples are parsed into a sequence of bits.

## Preliminaries

- Build the scripts with `make`.
- Make sure you are using the default system configuration with Turbo Boost enabled (`../scripts/set-variable-pstate.sh`).

## Collect traces

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
Then, run the following command.

```sh
./run-all-covert.sh
```

This script runs a covert channel test with the sender transmitting alternating bits to the receiver.
The default INTERVAL is 100000000 cycles (bandwidth of 30 bps), but you can use a different interval by passing it as an argument to the script.

## Plot/parse traces

To plot a sample of the traces (into `plot/covert-channel-bits.pdf`), run the following (with the correct ${INTERVAL}):
```sh
python plot-channel-bits-figure.py out/receiver-contention.out ${INTERVAL}
```

To print the number of errors over 8000 bits transmitted (8 kB), run the following (with the correct ${INTERVAL}):
```sh
python print-errors.py out/receiver-contention.out ${INTERVAL}
```

Depending on the characteristics of your machine, you might have to customize the `print-errors.py` script and the way it classifies ones and zeros (look for the `FIXME` comments).
Also, if you want to test the transmission of random bits instead of alternating 1s and 0s, you can set the respective variable in `sender.c` and `print-errors.py` and repeat the experiment.