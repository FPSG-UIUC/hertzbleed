import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from matplotlib.ticker import MaxNLocator
import seaborn as sns
import sys
import re
import os
import numpy as np
import matplotlib.pyplot as plt


# Density Plot and Histogram
# https://towardsdatascience.com/histograms-and-density-plots-in-python-f6bda88f5ac0
def plot_pdf(datas, labels):
    for data, label in zip(datas, labels):
        sns.distplot(data, label=label, hist=True, kde=True, bins=25)


# Prepare clean output directory
try:
    remove_tree('plot')
except:
    pass
out_dir = 'plot'
try:
    os.makedirs(out_dir)
except:
    pass

low = float(sys.argv[1])
high = float(sys.argv[2])
iteration = int(sys.argv[3])

key_list = []

with open("bit_recovered.txt", 'r') as key_file:
    for line in key_file:
        key_list.append(int(line.strip()))


swap_1 = []
swap_0 = []
times = []
swaps = []
for target_bit in range(0, 365):
    #target_bit = int(filename[filename.find("remote/")+7:filename.find(".txt")])
    filename = "./remote_result/"+str(target_bit)+".txt"
    # print(target_bit)
    my_time = []
    with open(filename, 'r') as result_file:
        for line in result_file:
            if("ALL_DURATION" in line):

                curr_time = line.strip().split()[1]
                curr_time_string = re.sub("[^\d\.]", "", curr_time)
                curr_time_float = float(curr_time_string)

                if("ms" not in line):
                    curr_time_float = curr_time_float * 1000

                if((curr_time_float < high) and (low < curr_time_float)):
                    my_time.append(curr_time_float)

    if(len(my_time)>iteration):
        my_time = my_time [ (len(my_time)-iteration):]
    result_time = np.median(my_time)
    times.append(result_time)
    prev_bit = 0
    if(target_bit == 0):
        prev_bit = 0
    else:
        prev_bit = key_list[target_bit-1]
    curr_bit = key_list[target_bit]
    swap = 1-(prev_bit == curr_bit)
    swaps.append(int(swap))
    if(swap == 0):
        swap_0.extend(my_time)
    else:
        swap_1.extend(my_time)

plt.figure(figsize=(3, 2))
plt.xlabel('Secret key bit index')
plt.ylabel('Time (ms)')
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
# ax1.set_ylim([low, high])
plt.plot(range(20), times[:20], linewidth=1, color="black")
# ax1.tick_params(axis='y', labelcolor=color)

# ylow, ymax = ax1.get_ylim()
colors = []
i = 0
for idx in range(20):
    if swaps[idx] == 1:
        colors.append("blue")
    else:
        colors.append("red")
    i += 1

a = []
a_times = []
b = []
b_times = []
colors_a = []
markers_a = []
colors_b = []
markers_b = []
i = 0
for idx in range(20):
    if swaps[idx] == 1:
        a.append(idx)
        a_times.append(times[idx])
        colors_a.append("tab:blue")
    else:
        b.append(idx)
        b_times.append(times[idx])
        colors_b.append("tab:red")
    i += 1

plt.scatter(a, a_times, color=colors_a, marker='X', zorder=2, label=r"$m_i \neq m_{i-1}$")
plt.scatter(b, b_times, color=colors_b, marker='o', zorder=2, label=r"$m_i = m_{i-1}$")

plt.legend(fontsize=7)
plt.tight_layout(pad=0.1)
plt.savefig("./plot/circl_swap_time_first20.pdf", dpi=300)
plt.clf()
plt.close()


plt.figure(figsize=(3, 2))
plt.xlabel('Secret key bit index')
plt.ylabel('Time (ms)')
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
# ax1.set_ylim([low, high])
plt.plot(range(len(times)-20, len(times)), times[len(times)-20:], linewidth=1, zorder=1, color="black")
# plt.tick_params(axis='y', labelcolor=color)

# ylow, ymax = ax1.set_ylim(ylow, ymax)

a = []
a_times = []
b = []
b_times = []
colors_a = []
markers_a = []
colors_b = []
markers_b = []
i = 0
for idx in range(len(swaps)-20, len(swaps)):
    if swaps[idx] == 1:
        a.append(idx)
        a_times.append(times[idx])
        colors_a.append("tab:blue")
    else:
        b.append(idx)
        b_times.append(times[idx])
        colors_b.append("tab:red")
    i += 1

plt.scatter(a, a_times, color=colors_a, marker='X', zorder=2, label=r"$m_i \neq m_{i-1}$")
plt.scatter(b, b_times, color=colors_b, marker='o', zorder=2, label=r"$m_i = m_{i-1}$")

plt.legend(fontsize=7)
plt.tight_layout(pad=0.1)
plt.savefig("./plot/circl_swap_time_last20.pdf", dpi=300)
plt.clf()
plt.close()


plt.figure(figsize=(3, 2))

# Prepare plot
datas = []
labels = []

datas.append(swap_0)
datas.append(swap_1)
labels.append(r"$m_i = m_{i-1}$")  # , $\overline{t}$: "+str(round(np.mean(swap_0), 2)))
labels.append(r"$m_i \neq m_{i-1}$")  # , $\overline{t}$: "+str(round(np.mean(swap_1), 2)))

plot_pdf(datas, labels)

# Show grid
#plt.grid(axis='y', alpha=0.75)

# Set labels
plt.xlabel("Time (ms)")
plt.ylabel('Probability density')

# Save plot to file
plt.legend(fontsize=7)
plt.tight_layout(pad=0.1)
plt.savefig("./plot/circl_distribution.pdf", dpi=300)
plt.clf()
plt.close()
