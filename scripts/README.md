# Scripts

We used these scripts to run all the leakage model experiments and parse their results.

## Description

- `set-fixed-pstate.sh`: disables Turbo Boost, effectively capping the P-state to the base frequency.
- `set-variable-pstate.sh`: re-enables Turbo Boost, allowing for variable frequencies in steady-state.
- `run-leakage-model-paper.sh`: runs all the experiments that are in Section 4 of the paper.
- `run-leakage-model-appendix.sh`: runs all the experiments that are in Appendix A.1 of the paper.
- `parse.py`: parses the results of the leakage model experiment (see READMEs in subfolders for example usage).

## How to reproduce the results from the paper

Assuming you machine is in the default system configuration:

1. Run `set-variable-pstate.sh` to ensure Turbo Boost is enabled.
2. Run `run-leakage-model-paper.sh` to collect the traces from Section 4 with variable frequency. 
Recall from `01` that, depending on your machine, you might have to run some additional background workload in order for these experiments to enter steady state.
1. Run `run-leakage-model-appendix.sh` to collect the traces from the Appendix with variable frequency.
2. Use the instructions in the READMEs of 03/04/05 to plot the _frequency_ figures.
3. Run `set-fixed-pstate.sh` to disable Turbo Boost.
4. Run `run-leakage-model-paper.sh` to collect the traces from Section 4 with fixed frequency.
5. Run `run-leakage-model-appendix.sh` to collect the traces from the Appendix with fixed frequency.
6. Use the instructions in the READMEs of 03/04/05 to plot the _power consumption_ figures.
