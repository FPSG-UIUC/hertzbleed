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
            energy_label_dict.setdefault(label, []).extend(energy_trace[100:])  # Exclude beginning

        if plot_freq:
            freq_label_dict.setdefault(label, []).extend(freq_trace[100:])      # Exclude beginning

        # Plot raw frequency trace if needed (useful for debug)
        if (plot_raw_freq):
            plt.figure(figsize=(20, 3.8))
            plt.plot(freq_trace)
            plt.savefig("./plot/freq_%s_%s.png" % (label, rept_idx))
            plt.clf()
            plt.close()

    # Parse energy data
    if plot_energy:
        print("\nEnergy Consumption Mean")

        # Prepare plot
        datas = []
        labels = []
        results = []

        # Parse energy data
        for label, trace in energy_label_dict.items():

            # Exclude negative samples (due to counter overflow)
            samples_positive = [x for x in trace if x > 0]

            # Get mean/std for each selector
            samples_mean = np.mean(samples_positive)
            samples_std = np.std(samples_positive)

            # Save mean/std
            print("%15s (%6d samples): %.15f +- %.15f J" % (label, len(trace), samples_mean, samples_std))
            results.append((label, samples_mean, samples_std))

            # Filter outliers (for the plot only)
            samples_filtered = []  # 2 std
            for sample in samples_positive:
                if abs(sample - samples_mean) <= 2 * samples_std:
                    samples_filtered.append(sample)

            # Store data for bars
            datas.append(samples_filtered)
            labels.append("{} ({} samples)".format(label, len(samples_filtered)))

        # Save means and stds to file
        with open(in_dir + "/energy.txt", 'w') as f:
            for label, mean, std in results:
                print("%s %.15f %.15f" % (label, mean, std), file=f)

        # Produce plot if asked
        # NOTE: these plots become unreadable when the number of selectors is >10
        if plot_histograms:
            plt.figure()   # 6.4, 4.8
            plot_pdf(datas, labels)
            plt.xlabel('Energy consumption (J)')
            plt.ylabel('Probability Density')
            plt.legend()
            plt.tight_layout()
            plt.savefig("./plot/hist-energy.png", dpi=300)
            plt.clf()

    # Parse frequency data
    if plot_freq:
        print("\nFrequency Mean")

        # Prepare plot
        minimum = 100000
        maximum = 0
        datas = []
        labels = []
        weights = []
        results = []

        # Parse data
        for label, trace in freq_label_dict.items():

            # Get mean/std for each selector
            samples_mean = np.mean(trace)
            samples_std = np.std(trace)

            # Save mean/std
            print("%15s (%6d samples): %d +- %d KHz (min %d max %d)" % (label, len(trace), samples_mean, samples_std, min(trace), max(trace)))
            results.append((label, samples_mean, samples_std))

            # Filter outliers (for the plot only)
            samples_filtered = []
            for sample in trace:
                if abs(sample - samples_mean) <= 2 * samples_std:
                    samples_filtered.append(sample / 1000000 + 0.05)    # the + 0.05 is because the hist takes [4.2, 4.3) as range and we want 4.299999 in 4.3

            # Store data for bins
            minimum = min(round(min(samples_filtered), 1), minimum)
            maximum = max(round(max(samples_filtered), 1), maximum)

            # Store data for bars
            datas.append(samples_filtered)
            labels.append("hw={}".format(label))
            weights.append(np.ones_like(samples_filtered)/float(len(samples_filtered)))

        # Save means and stds to file
        with open(in_dir + "/frequency.txt", 'w') as f:
            for label, mean, std in results:
                print("%s %d %d" % (label, mean, std), file=f)

        # Produce plot if asked
        # NOTE: these plots become unreadable when the number of selectors is >10
        if plot_histograms:

            # Plot all data
            plt.figure()  # 6.4, 4.8
            bins = np.arange(minimum, maximum + 0.1, 0.1)
            _, bins, _ = plt.hist(datas, alpha=0.5, bins=bins, weights=weights, label=labels, align="left")
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(0.1))
            plt.xlabel('Frequency (GHz)')
            plt.ylabel('Probability Density')
            plt.legend()
            plt.tight_layout()
            plt.savefig("./plot/hist-freq.png", dpi=300)
            plt.clf()


if __name__ == "__main__":
    main()
