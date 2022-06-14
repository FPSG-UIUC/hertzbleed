import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys

filename = sys.argv[1]

my_file = open(filename, 'r')

swap0 = []
swap1 = []
swap_value = 0
for line in my_file:
    if("target_swap" in line):
        swap_value = int(line.split()[1])
    if("sike took about" in line):
        curr_time = line.split()[3]
        curr_time_float = float(curr_time)

        if(swap_value == 0):
            swap0.append(curr_time_float)
        if(swap_value == 1):
            swap1.append(curr_time_float)

filter_swap0 = []
filter_swap1 = []
swap0_mean = np.mean(swap0)
swap1_mean = np.mean(swap1)
swap0_std = np.std(swap0)
swap1_std = np.std(swap1)

for sample in swap0:
    if abs(sample - swap0_mean) <= 1 * swap0_std:
        filter_swap0.append(sample)

for sample in swap1:
    if abs(sample - swap1_mean) <= 1 * swap1_std:
        filter_swap1.append(sample)

fig, ax = plt.subplots()

swap_1_label = r"$m_i \neq m_{i-1}$"
swap_0_label = r"$m_i = m_{i-1}$"

sns.distplot(filter_swap0, bins=50, label=swap_0_label, hist_kws={'edgecolor': 'black'}, color='blue', kde=False)
sns.distplot(filter_swap1, bins=50, label=swap_1_label, hist_kws={'edgecolor': 'black'}, color='red', kde=False)

plt.legend()

plt.xlabel("Time(s)")
plt.ylabel("Counts")
plt.savefig("./plot/local-time-plot.jpeg")
