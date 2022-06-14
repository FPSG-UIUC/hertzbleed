import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import argparse
import seaborn as sns
import glob
import os
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import numpy as np


def parse_file(fn):
    energy = []
    freq = []
    with open(fn) as f:
        for line in f:
            a, b = line.strip().split()
            energy.append(float(a))
            freq.append(int(b))

    return np.array(energy), np.array(freq)


# Density Plot and Histogram
# https://towardsdatascience.com/histograms-and-density-plots-in-python-f6bda88f5ac0
def plot_pdf(datas, labels):
    for data, label in zip(datas, labels):
        sns.distplot(data, label=label, hist=True, kde=True, bins=int(180/5))


def main():

    # Prepare output directory
    try:
        os.makedirs('plot')
    except:
        pass

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--freq', action='store_true')
    parser.add_argument('--energy', action='store_true')
    parser.add_argument('--hist', action='store_true')
    parser.add_argument('folder')
    args = parser.parse_args()
    in_dir = args.folder
    plot_raw_freq = args.raw
    plot_freq = args.freq
    plot_energy = args.energy
    plot_histograms = args.hist

    # For histograms
    energy_label_dict = {}
    freq_label_dict = {}

    # Read data
    #    ./out/all_%s_%04d.out
    out_files = sorted(glob.glob(in_dir + "/all_*"))
    for f in out_files:
        label = "_".join(f.split("/")[-1].split(".")[0].split("_")[1:-1])
        rept_idx = f.split("/")[-1].split(".")[0].split("_")[-1]
        energy_trace, freq_trace = parse_file(f)

        if plot_energy:
            energy_label_dict.setdefault(label, []).extend(energy_trace)

        if plot_freq:
            freq_label_dict.setdefault(label, []).extend(freq_trace)

        # FIXME: Change to True to plot frequency
        if (plot_raw_freq):
            plt.figure(figsize=(20, 3.8))
            plt.plot(freq_trace)
            plt.savefig("./plot/freq_%s_%s.png" % (label, rept_idx))
            plt.clf()
            plt.close()

    # Parse energy data
    if plot_energy:
        print("\nEnergy Consumption Mean")

        # Prepare sike plot
        power_swap = {}
        power_swap[0] = []
        power_swap[1] = []

        # Parse energy data
        for label, trace in energy_label_dict.items():

            # Exclude negative samples (due to counter overflow)
            samples_positive = [x for x in trace if x > 0]

            # Get mean/std for each selector
            samples_mean = np.mean(samples_positive)
            samples_std = np.std(samples_positive)

            # Save mean/std
            print("%15s (%6d samples): %.15f +- %.15f J" % (label, len(trace), samples_mean, samples_std))

            # Filter outliers (for the plot only)
            samples_filtered = []  # 2 std
            for sample in samples_positive:
                if abs(sample - samples_mean) <= 2 * samples_std:
                    power = sample / 0.001      # 0.001 is to convert to power since we sample energy every 1ms
                    samples_filtered.append(power)

            # Process sike plot
            label_list = label.split("_")
            curr_swap = swap[int(label_list[1])][int(label_list[2])]
            if(int(label_list[0]) == 1):
                curr_swap = 1 - curr_swap
            power_swap[curr_swap].extend(samples_filtered)

        # Print mean
        print()
        print("m_i == m_{i-1}: %.15f +- %.15f W" % (np.mean(power_swap[0]), np.std(power_swap[0])))
        print("m_i != m_{i-1}: %.15f +- %.15f W" % (np.mean(power_swap[1]), np.std(power_swap[1])))

        if plot_histograms:
            key = [r"$m_i = m_{i-1}$", r"$m_i \neq m_{i-1}$"]
            value = [power_swap[0], power_swap[1]]
            plt.figure(figsize=(3, 2))  # 6.4, 4.8
            plot_pdf(value, key)
            plt.xlabel('Power consumption (W)')
            plt.ylabel('Probability density')
            plt.legend(fontsize=7)
            plt.tight_layout(pad=0.1)
            plt.savefig("./plot/circl-local-hist-energy.pdf", dpi=300)
            plt.clf()

    # Parse frequency data
    if plot_freq:
        print("\nFrequency Mean")

        # Prepare sike plot
        minimum = 100000
        maximum = 0
        freq_swap = {}
        freq_swap[0] = []
        freq_swap[1] = []
        weight_swap = {}
        weight_swap[0] = []
        weight_swap[1] = []

        # Parse data
        for label, trace in freq_label_dict.items():

            # Get mean/std for each selector
            samples_mean = np.mean(trace)
            samples_std = np.std(trace)

            # Save mean/std
            print("%15s (%6d samples): %d +- %d KHz (min %d max %d)" % (label, len(trace), samples_mean, samples_std, min(trace), max(trace)))

            # Filter outliers (for the plot only)
            samples_filtered = []
            for sample in trace:
                if abs(sample - samples_mean) <= 2 * samples_std:
                    samples_filtered.append(sample / 1000000 + 0.05)    # the + 0.05 is because the hist takes [4.2, 4.3) as range and we want 4.299999 in 4.3

            # Store data for bins
            minimum = min(round(min(samples_filtered), 1), minimum)
            maximum = max(round(max(samples_filtered), 1), maximum)

            # Process sike plot
            label_list = label.split("_")
            curr_swap = swap[int(label_list[1])][int(label_list[2])]
            if(int(label_list[0]) == 1):
                curr_swap = 1-curr_swap
            freq_swap[curr_swap].extend(samples_filtered)
            weight_swap[curr_swap].extend(np.ones_like(samples_filtered)/float(len(samples_filtered)))

        # Print mean
        print()
        print("m_i == m_{i-1}: %.15f +- %.15f KHz (*)" % (np.mean(freq_swap[0]), np.std(freq_swap[0])))     # These means are shifted by 0.05
        print("m_i != m_{i-1}: %.15f +- %.15f KHz (*)" % (np.mean(freq_swap[1]), np.std(freq_swap[1])))     # These means are shifted by 0.05

        if plot_histograms:
            key = [r"$m_i = m_{i-1}$", r"$m_i \neq m_{i-1}$"]
            value = [freq_swap[0], freq_swap[1]]
            value_weight = [weight_swap[0], weight_swap[1]]

            # Plot all data
            plt.figure(figsize=(3, 2))  # 6.4, 4.8
            bins = np.arange(minimum, maximum + 0.1, 0.1)  # FIXME CIRCL
            _, bins, _ = plt.hist(value, alpha=0.5, bins=bins, weights=value_weight, label=key, align="left", density=True)
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
            plt.xlabel('Frequency (GHz)')
            plt.ylabel('Probability density')
            plt.legend(fontsize=7)
            plt.tight_layout(pad=0.1)
            plt.savefig("./plot/circl-local-hist-freq.pdf", dpi=300)
            plt.clf()


if __name__ == "__main__":
    swap = {}
    for x in range(1, 11):
        swap[x] = {}

    swap[1][2] = 0
    swap[1][150] = 0
    swap[2][5] = 1
    swap[2][50] = 1
    swap[3][9] = 1
    swap[3][70] = 1
    swap[4][13] = 1
    swap[4][80] = 0
    swap[5][15] = 0
    swap[5][90] = 0
    swap[6][45] = 0
    swap[6][100] = 0
    swap[7][150] = 0
    swap[7][234] = 1
    swap[8][180] = 1
    swap[8][275] = 0
    swap[9][150] = 1
    swap[9][190] = 0
    swap[10][170] = 0
    swap[10][270] = 0

    main()
