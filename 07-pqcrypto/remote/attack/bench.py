import sys

print("#!/bin/bash")
start_index = int(sys.argv[1])
connection = int(sys.argv[2])
iteration = int(sys.argv[3])

print("../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT "+str(start_index)+" "+str(connection)+" "+str(iteration)+" bit_recovered.txt")

for i in range(start_index, 365):
    print("../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT "+str(i)+" "+str(connection)+" "+str(iteration)+" bit_recovered.txt >> remote_result/"+str(i)+".txt")
    print("python3 data.py "+str(i)+".txt")
print("../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT "+str(365)+" 300 0 bit_recovered.txt")
