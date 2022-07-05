import matplotlib.pyplot as plt
import numpy as np
import sys
import subprocess

# FIXME
low = float(5.0)
high = float(5.5)
repeat_low = 5.315
repeat_high = 5.345

my_time = []
filename = "remote_result/"+sys.argv[1]

with open(filename, "r") as result_file:
    for line in result_file:
        if("sike took about" in line):
            curr_time = line.split()[3]
            curr_time_float = float(curr_time)
            if((curr_time_float < high) and (low < curr_time_float)):
                my_time.append(curr_time_float)


# reexecute the experiment if the median fall between an undecidable range

result_time = np.median(my_time)
while((result_time >= repeat_low) and (result_time <= repeat_high)):
    print(filename)
    print(np.mean(my_time))
    print(np.median(my_time))

    process = subprocess.Popen(["rm", "remote_result/"+sys.argv[1]], stdout=subprocess.PIPE)
    process.wait()
    print("finish remove")
    target_bit = sys.argv[1][:sys.argv[1].find(".txt")]

    with open(filename, "w") as log_file:
        process = subprocess.Popen(["../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT", target_bit, "1000", "400", "bit_recovered.txt", ">>", "remote_result/"+sys.argv[1]], stdout=log_file)
        process.wait()
    print("finish wait")
    my_time = []
    with open(filename, "r") as result_file_again:
        for line in result_file_again:
            if("sike took about" in line):
                curr_time = line.split()[3]
                curr_time_float = float(curr_time)
                if((curr_time_float < high) and (low < curr_time_float)):
                    my_time.append(curr_time_float)
    print(len(my_time))
    result_time = np.median(my_time)


swap = 0
if(result_time < repeat_low):
    swap = 1

last_line = "0"

my_bit = 0
same_count = 0
with open("bit_recovered.txt", "r") as f:
    for line in f:
        curr_bit = int(line.strip())
        if(my_bit == curr_bit):
            same_count = same_count + 1
        else:
            same_count = 0
        if(same_count == 64):
            print("REDO ATTACK!!!!!!!!!!! FIRST BIT IS DEFINITELY WRONG")
        my_bit = curr_bit
        last_line = line
f.close()


prev_bit = int(last_line.strip())

next_bit = 0
if(swap == 0):
    next_bit = prev_bit
else:
    if(prev_bit == 0):
        next_bit = 1
    if(prev_bit == 1):
        next_bit = 0
print(filename)
print(np.mean(my_time))
print(len(my_time))
print(np.median(my_time))
print(prev_bit)
print(next_bit)
f = open("bit_recovered.txt", "a")
f.write(str(next_bit))
f.write("\n")
f.close()
