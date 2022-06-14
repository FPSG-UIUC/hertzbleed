# Overview

This repository contains the source code to reproduce the experiments of the paper:

- [_Hertzbleed: Turning Power Side-Channel Attacks Into Remote Timing Attacks on x86_][paper] (__USENIX 2022__)

**NB:** This source code is CPU-specific.

## Tested Setup

The code of this repo was fully tested on a **bare-metal** machine with an **Intel i7-9700 CPU**.
The machine was a stock Dell machine, running **Ubuntu 20.04**.
We do not guarantee that this code works in virtualized environments, on other CPUs, on custom machines, or with other operating systems.
Running this code on other CPUs (e.g., see [the paper][paper] for a table with the models we tested), will likely require changing some of the code.

## Materials

This repository contains the following materials:
- `01-leakage-channel-workloads`: contains the code that we used to test if the scaling of P-states leaks information about the current workload (Figure 1).
- `02-leakage-channel-data`: contains the code that we used to test if the scaling of P-states leaks information about the data being processed (Figure 2).
- `03-leakage-model-hd`: contains the code that we used to test the HD leakage model (Figures 4, 14).
- `04-leakage-model-hw`: contains the code that we used to test the HW leakage model (Figures 5-7, 15-17).
- `05-leakage-model-hd_hw`: contains the code that we used to test the additivity of HD and HW (Figure 8).
- `06-circl`: contains the code that we used to perform the SIKE attack on the circl library.
- `07-pqcrypto`: contains the code that we used to perform the SIKE attack on the pqcrypto-sidh library.
- `08-kaslr`: contains the code that we used to perform the timer-free KASLR break.
- `09-cc`: contains the code that we used to test a timer-free covert channel.
- `scripts`: contains scripts that can be used to run all the leakage model experiments and parse their results.
- `util`: contains scripts that can be used to run all the leakage model experiments and parse their results.

We suggest that you run these experiments in order (from 01 to 09).
In the paper, we ran some experiments in two setups: with the default system configuration (Turbo Boost on) or with the P-state capped at the base frequency (Turbo Boost off).
We provide the scripts to switch between these 2 setups in the `scripts` folder.

## Preliminaries

- Install `stress-ng` using `sudo apt install -y stress-ng`.
- Set up a Python virtual environment as follows: 
```sh
virtualenv -p python3 venv
source venv/bin/activate
pip install seaborn
```

## Citation

If you make any use of this code for academic purposes, please cite the paper:

```tex
@inproceedings{wan2022hertzbleed,
    author = {Yingchen Wang and Riccardo Paccagnella and Elizabeth He and Hovav Shacham and Christopher W. Fletcher and David Kohlbrenner},
    title = {Hertzbleed: Turning Power Side-Channel Attacks Into Remote Timing Attacks on x86},
    booktitle = {Proc.\ of the USENIX Security Symposium (USENIX)},
    year = {2022},
}
```

[paper]: https://www.hertzbleed.com/herzbleed.pdf
