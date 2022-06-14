import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import argparse
import numpy as np
import os
import copy


def bitfield(n):
    bit_list = [int(digit) for digit in bin(n)[2:]]  # [2:] to chop off the "0b" part
    if(len(bit_list) < 8):
        for x in range(8 - len(bit_list)):
            bit_list.insert(0, 0)
    return bit_list


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
                hw_left, shift_left = selector.split("_")[0], selector.split("_")[2]
                data.setdefault(int(hw_left), {})
                data[int(hw_left)][int(shift_left)] = (int(mean), int(std))

        if 100 in data:
            independence = {}
            for x in range(256):
                all_bytes = bitfield(x)
                for byte in range(8):
                    seven_bytes = copy.deepcopy(all_bytes)
                    seven_bytes.pop(byte)
                    seven_bytes = tuple(seven_bytes)
                    independence.setdefault(byte, {})
                    independence[byte].setdefault(seven_bytes, {})
                    if (all_bytes[byte] == 0):
                        independence[byte][seven_bytes][0] = data[x+100][0]
                    else:
                        independence[byte][seven_bytes][1] = data[x+100][0]

            byte_mean = {}
            byte_std = {}
            for byte in independence:
                deltas = []
                for seven_bytes in independence[byte]:
                    deltas.append(independence[byte][seven_bytes][1][0] - independence[byte][seven_bytes][0][0])

                deltas.sort()
                deltas_filtered = deltas[10:-10]
                byte_mean[byte] = np.mean(deltas_filtered)
                byte_std[byte] = np.std(deltas_filtered)

            key, mean, std = [], [], []
            for x in byte_mean:
                key.append(7 - x)
                mean.append(byte_mean[x] / 1000000)  # / 1000000 is to convert to GHz
                std.append(byte_std[x] / 1000000)  # / 1000000 is to convert to GHz

            plt.figure(figsize=(3, 2))
            plt.errorbar(key, mean, yerr=std, fmt='o', ms=3)
            plt.xlabel('Byte index')
            plt.ylabel('Δ Frequency (GHz)')
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
            plt.tight_layout(pad=0.1)
            plt.savefig("./plot/" + args.figname + "-independence.pdf", dpi=300)
            plt.clf()

        plt.figure(figsize=(3, 2))

        x, y = [], []
        for hamming in range(65):
            if hamming in data:
                x.append(hamming)
                y.append(data[hamming][0][0] / 1000000)  # / 1000000 is to convert to GHz
        plt.scatter(x, y, label="From LSB", s=3)

        x, y = [], []
        for hamming in range(65):
            if hamming in data:
                x.append(hamming)
                y.append(data[hamming][64-hamming][0] / 1000000)  # / 1000000 is to convert to GHz
        plt.scatter(x, y, label="From MSB", s=3)

        plt.xlabel('Hamming weight')
        plt.ylabel('Frequency (GHz)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + ".pdf", dpi=300)
        plt.clf()

    if (energy_file):
        data = {}
        with open(energy_file + "/energy.txt") as f:
            for line in f:
                selector, mean, std = line.strip().split()
                hw_left, shift_left = selector.split("_")[0], selector.split("_")[2]
                data.setdefault(int(hw_left), {})
                data[int(hw_left)][int(shift_left)] = (float(mean), float(std))

        independence = {}
        for x in range(256):
            all_bytes = bitfield(x)
            for byte in range(8):
                seven_bytes = copy.deepcopy(all_bytes)
                seven_bytes.pop(byte)
                seven_bytes = tuple(seven_bytes)
                independence.setdefault(byte, {})
                independence[byte].setdefault(seven_bytes, {})
                if (all_bytes[byte] == 0):
                    independence[byte][seven_bytes][0] = data[x+100][0]
                else:
                    independence[byte][seven_bytes][1] = data[x+100][0]

        byte_mean = {}
        byte_std = {}
        for byte in independence:
            deltas = []
            for seven_bytes in independence[byte]:
                deltas.append(independence[byte][seven_bytes][1][0] - independence[byte][seven_bytes][0][0])

            deltas.sort()
            deltas_filtered = deltas[10:-10]
            byte_mean[byte] = np.mean(deltas_filtered)
            byte_std[byte] = np.std(deltas_filtered)

        key, mean, std = [], [], []
        for x in byte_mean:
            key.append(7 - x)
            mean.append(byte_mean[x] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
            std.append(byte_std[x] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms

        plt.figure(figsize=(3, 2))
        plt.errorbar(key, mean, yerr=std, fmt='o', ms=3)
        plt.xlabel('Byte index')
        plt.ylabel('Δ Power (W)')
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + "-independence.pdf", dpi=300)
        plt.clf()

        plt.figure(figsize=(3, 2))

        x, y = [], []
        for hamming in range(65):
            if hamming in data:
                x.append(hamming)
                y.append(data[hamming][0][0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
        plt.scatter(x, y, label="From LSB", s=3)

        x, y = [], []
        for hamming in range(65):
            if hamming in data:
                x.append(hamming)
                y.append(data[hamming][64-hamming][0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
        plt.scatter(x, y, label="From MSB", s=3)

        plt.xlabel('Hamming weight')
        plt.ylabel('Power (W)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + ".pdf", dpi=300)
        plt.clf()


if __name__ == "__main__":
    main()
