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
        data_ones = {}
        data_zeros = {}
        with open(freq_file + "/frequency.txt") as f:
            for line in f:
                selector, mean, std = line.strip().split()
                hw_left, shift_left = selector.split("_")[0], selector.split("_")[2]
                if int(shift_left) >= 0:
                    data_ones.setdefault(int(hw_left), {})
                    data_ones[int(hw_left)][int(shift_left)] = (int(mean), int(std))
                else:
                    data_zeros.setdefault(int(hw_left), {})
                    data_zeros[int(hw_left)][-int(shift_left)] = (int(mean), int(std))

        plt.figure(figsize=(3, 2))

        for hamming in data_ones:
            x, y = [], []
            for shift in data_ones[hamming]:
                x.append(shift)
                y.append(data_ones[hamming][shift][0] / 1000000)  # / 1000000 is to convert to GHz
            plt.scatter(x, y, label=str(hamming) + " ones", s=3)

        plt.xlabel('Shift offset')
        plt.ylabel('Frequency (GHz)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + "_ones.pdf", dpi=300)
        plt.clf()

        plt.figure(figsize=(3, 2))

        for hamming in data_zeros:
            x, y = [], []
            for shift in data_zeros[hamming]:
                x.append(shift)
                y.append(data_zeros[hamming][shift][0] / 1000000)  # / 1000000 is to convert to GHz
            plt.scatter(x, y, label=str(hamming) + " zeros", s=3)

        plt.xlabel('Shift offset')
        plt.ylabel('Frequency (GHz)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + "_zeros.pdf", dpi=300)
        plt.clf()

    if (energy_file):
        data_ones = {}
        data_zeros = {}
        with open(energy_file + "/energy.txt") as f:
            for line in f:
                selector, mean, std = line.strip().split()
                hw_left, shift_left = selector.split("_")[0], selector.split("_")[2]
                if int(shift_left) >= 0:
                    data_ones.setdefault(int(hw_left), {})
                    data_ones[int(hw_left)][int(shift_left)] = (float(mean), float(std))
                else:
                    data_zeros.setdefault(int(hw_left), {})
                    data_zeros[int(hw_left)][-int(shift_left)] = (float(mean), float(std))

        plt.figure(figsize=(3, 2))

        for hamming in data_ones:
            x, y = [], []
            for shift in data_ones[hamming]:
                x.append(shift)
                y.append(data_ones[hamming][shift][0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
            plt.scatter(x, y, label=str(hamming) + " ones", s=3)

        plt.xlabel('Shift offset')
        plt.ylabel('Power (W)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + "_ones.pdf", dpi=300)
        plt.clf()

        plt.figure(figsize=(3, 2))

        for hamming in data_zeros:
            x, y = [], []
            for shift in data_zeros[hamming]:
                x.append(shift)
                y.append(data_zeros[hamming][shift][0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
            plt.scatter(x, y, label=str(hamming) + " zeros", s=3)

        plt.xlabel('Shift offset')
        plt.ylabel('Power (W)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + "_zeros.pdf", dpi=300)
        plt.clf()


if __name__ == "__main__":
    main()
