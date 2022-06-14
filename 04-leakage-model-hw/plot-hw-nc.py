import matplotlib.pyplot as plt
import argparse
import os


def main():

    # Prepare output directory
    try:
        os.makedirs('plot')
    except:
        pass

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--freq')
    parser.add_argument('--energy')
    parser.add_argument('figname')
    args = parser.parse_args()
    freq_file = args.freq
    energy_file = args.energy

    if (freq_file):
        data = {}
        with open(freq_file + "/frequency.txt") as f:
            for line in f:
                selector, mean, std = line.strip().split()
                data[int(selector)] = (int(mean), int(std))

        x, y = [], []
        for key, val in data.items():
            x.append(key)
            y.append(val[0] / 1000000)  # / 1000000 is to convert to GHz

        plt.figure(figsize=(3, 2))
        plt.scatter(x, y, s=3)
        plt.xlabel('Hamming weight')
        plt.ylabel('Frequency (GHz)')
        # plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + ".pdf", dpi=300)
        plt.clf()

    if (energy_file):
        data = {}
        with open(energy_file + "/energy.txt") as f:
            for line in f:
                selector, mean, std = line.strip().split()
                data[int(selector)] = (float(mean), float(std))

        x, y = [], []
        for key, val in data.items():
            x.append(key)
            y.append(val[0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms

        plt.figure(figsize=(3, 2))
        plt.scatter(x, y, s=3)
        plt.xlabel('Hamming weight')
        plt.ylabel('Power (W)')
        # plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + ".pdf", dpi=300)
        plt.clf()


if __name__ == "__main__":
    main()
