import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
import sys


try:
    remove_tree('plot')
except:
    pass
out_dir = 'plot'
try:
    os.makedirs(out_dir)
except:
    pass


filename_random = sys.argv[1]
filename = sys.argv[2]
low = float(sys.argv[3])
high = float(sys.argv[4])


my_file_random = open(filename_random, 'r')
my_file = open(filename, 'r')
random_data = []
attack_data = []


for line in my_file_random:
    if("sike took about" in line):
        curr_time = line.split()[3]
        curr_time_float = float(curr_time)
        if((curr_time_float < high) and (low < curr_time_float)):
            random_data.append(curr_time_float)
            
for line in my_file:
    if("sike took about" in line):
        curr_time = line.split()[3]
        curr_time_float = float(curr_time)
        if((curr_time_float < high) and (low < curr_time_float)):
            attack_data.append(curr_time_float)
            
            
fig, ax = plt.subplots()

nospeedup = "no speedup"
unknown = "unknown"

sns.distplot(random_data, bins=50, label=nospeedup, hist_kws={'edgecolor': 'black'}, color='blue', kde=False)
sns.distplot(attack_data, bins=50, label=unknown, hist_kws={'edgecolor': 'black'}, color='red', kde=False)

print(nospeedup+" mean: "+str(np.mean(random_data)))
print(unknown+" mean: "+str(np.mean(attack_data)))
print(nospeedup+" median: "+str(np.median(random_data)))
print(unknown+" median: "+str(np.median(attack_data)))
print(nospeedup+" std: "+str(np.std(random_data)))
print(unknown+" std: "+str(np.std(attack_data)))
print(nospeedup+" length: "+str(len(random_data)))
print(unknown+" length: "+str(len(attack_data)))

plt.legend()

plt.xlabel("Time(ms)")
plt.ylabel("Counts")
plt.savefig("./plot/attack_compare.jpeg")
