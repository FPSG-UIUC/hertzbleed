import sys

print("#!/bin/bash")
connection = int(sys.argv[1])
iteration = int(sys.argv[2])

print("../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT "+str(50)+" "+str(connection)+" "+str(iteration)+" bit_recovered_nospeedup.txt")

for i in range(50,100):
    print("../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT "+str(i)+" "+str(connection)+" "+str(iteration)+" bit_recovered_nospeedup.txt >> output_nospeedup.txt")
    
    
