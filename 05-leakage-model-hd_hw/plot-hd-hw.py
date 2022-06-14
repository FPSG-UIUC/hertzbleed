import matplotlib.pyplot as plt
import argparse
import os


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
                selectors = selector.split("_")
                hw_first, hw_second, shift_first = int(selectors[0]), int(selectors[1]), int(selectors[2])

                if hw_first == 16 and shift_first == 0:
                    data.setdefault("A", {})
                    data["A"][hw_second] = (int(mean), int(std))
                if((hw_first == 16) and (shift_first == 48)):
                    data.setdefault("B", {})
                    data["B"][hw_second] = (int(mean), int(std))
                if((hw_first == 32) and (shift_first == 0)):
                    data.setdefault("C", {})
                    data["C"][hw_second] = (int(mean), int(std))
                if((hw_first == 32) and (shift_first == 32)):
                    data.setdefault("D", {})
                    data["D"][hw_second] = (int(mean), int(std))

        plt.figure(figsize=(3, 2))

        for letter in data:
            x, y = [], []
            for hamming in data[letter]:
                x.append(hamming)
                y.append(data[letter][hamming][0] / 1000000)  # / 1000000 is to convert to GHz
            plt.scatter(x, y, label=letter, s=3)

        plt.xlabel('HW of SECOND')
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
                selectors = selector.split("_")
                hw_first, hw_second, shift_first = int(selectors[0]), int(selectors[1]), int(selectors[2])

                if hw_first == 16 and shift_first == 0:
                    data.setdefault("A", {})
                    data["A"][hw_second] = (float(mean), float(std))
                if((hw_first == 16) and (shift_first == 48)):
                    data.setdefault("B", {})
                    data["B"][hw_second] = (float(mean), float(std))
                if((hw_first == 32) and (shift_first == 0)):
                    data.setdefault("C", {})
                    data["C"][hw_second] = (float(mean), float(std))
                if((hw_first == 32) and (shift_first == 32)):
                    data.setdefault("D", {})
                    data["D"][hw_second] = (float(mean), float(std))

        plt.figure(figsize=(3, 2))

        for letter in data:
            x, y = [], []
            for hamming in data[letter]:
                x.append(hamming)
                y.append(data[letter][hamming][0] / 0.001)		# 0.001 is to convert to power since we sample energy every 1ms
            plt.scatter(x, y, label=letter, s=3)

        plt.xlabel('HW of SECOND')
        plt.ylabel('Power (W)')
        plt.legend(fontsize=7)
        plt.tight_layout(pad=0.1)
        plt.savefig("./plot/" + args.figname + ".pdf", dpi=300)
        plt.clf()


if __name__ == "__main__":
    main()
