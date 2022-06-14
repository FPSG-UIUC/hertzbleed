import argparse
import glob
import os
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import numpy as np
from distutils.dir_util import remove_tree


# -------------------------------------------------------------------------------------------------------------------
# Parsing Functions
# -------------------------------------------------------------------------------------------------------------------

def parse_energy(fn):
    energy = []
    with open(fn) as f:
        for line in f:
            a = line.strip()
            energy.append(float(a))
    return np.array(energy)


def parse_freq(fn):
    freq = []
    with open(fn) as f:
        for line in f:
            c = line.strip()
            freq.append(int(c))
    return np.array(freq)


# -------------------------------------------------------------------------------------------------------------------

def main():

    # Prepare output directory
    try:
        remove_tree('plot')
    except:
        pass
    try:
        os.makedirs('plot')
    except:
        pass

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    in_dir = args.folder

    # Read data
    #    ./out/all_%s_%04d.out
    energy_files = sorted(glob.glob(in_dir + "/energy_*"), reverse=True)
    freq_files = sorted(glob.glob(in_dir + "/freq_*"), reverse=True)

    ylowf, ymaxf = 0, 0
    ylowe, ymaxe = 0, 0

    for f, g in zip(energy_files, freq_files):

        # Parse trace
        raw_energy_trace = parse_energy(f)
        raw_freq_trace = parse_freq(g)

        # Exclude overflows in energy counters and convert to power
        power_trace = []
        prev_sample = 0
        thres = np.percentile(raw_energy_trace, 99)     # Exclude outliers
        for i, x in enumerate(raw_energy_trace[10:]):   # Exclude first 10 samples
            if x > 0 and x <= thres:
                power_sample = x / 0.005  		# 0.005 is to convert to power since we sample energy every 5ms
                power_trace.append(power_sample)
                prev_sample = power_sample
            else:
                power_trace.append(prev_sample)

        # Convert freq trace to GHz
        freq_trace = (raw_freq_trace[10:] / 1000000)  		# 1000000 is to convert to GHz

        # Convert x axis to seconds
        x_axis = []
        for i in range(len(freq_trace)):
            x_axis.append(i / 200)

        # Generate figure for both freq and power
        plt.figure(figsize=(3.2, 2.6))

        # Plot frequency
        plt.subplot(2, 1, 1)
        color = "tab:blue"
        # plt.ylabel('Frequency (GHz)')
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.1))
        plt.plot(x_axis, freq_trace, linewidth=0.2, color=color, label="Frequency (GHz)")
        plt.legend(fontsize=7, loc='upper right')
        # plt.grid(axis='y')
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=True,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False)  # labels along the bottom edge are off

        # Get yrange for the first plot
        if ylowf == 0:
            ylowf, ymaxf = plt.gca().get_ylim()
        else:
            plt.ylim(ylowf, ymaxf)

        # Plot power
        plt.subplot(2, 1, 2)
        color = "tab:red"
        # plt.ylabel('Power (W)')
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))
        plt.plot(x_axis, power_trace, linewidth=0.2, color=color, label="Power (W)", linestyle="--")
        plt.legend(fontsize=7, loc='upper right')

        # Get yrange for the first plot
        if ylowe == 0:
            ylowe, ymaxe = plt.gca().get_ylim()
        else:
            plt.ylim(ylowe, ymaxe)

        # Shared x axis
        plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # No decimal places
        plt.xlabel('Time (s)')

        # Save file
        plt.tight_layout(pad=0, w_pad=0.5, h_pad=.5)
        plt.savefig("plot/stress_%s.pdf" % "_".join(f.split("/")[-1].split(".")[0].split("_")[1:]))
        plt.close()
        plt.clf()


if __name__ == "__main__":
    main()
