import sys

print("#!/bin/bash")
start_index = int(sys.argv[1])
connection = int(sys.argv[2])
iteration = int(sys.argv[3])

print("../../circl/dh/sidh/POC_ATTACK/sike_client "+str(connection)+" "+str(iteration)+" bit_recovered.txt "+str(start_index))
for i in range(start_index, 365):
    print("../../circl/dh/sidh/POC_ATTACK/sike_client "+str(connection)+" "+str(iteration)+" bit_recovered.txt "+str(i)+" >> remote_result/"+str(i)+".txt")
    print("python3 data.py "+str(i)+".txt")
print("../../circl/dh/sidh/POC_ATTACK/sike_client 300 0 bit_recovered.txt 365")
