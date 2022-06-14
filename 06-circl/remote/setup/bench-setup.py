import sys

print("#!/bin/bash")
connection = int(sys.argv[1])
iteration = int(sys.argv[2])

print("../../circl/dh/sidh/POC_ATTACK/sike_client "+str(connection)+" "+str(iteration)+" bit_recovered_nospeedup.txt "+str(50))
for i in range(50,100):
    print("../../circl/dh/sidh/POC_ATTACK/sike_client "+str(connection)+" "+str(iteration)+" bit_recovered_nospeedup.txt "+str(i)+" >> output_nospeedup.txt")
    
