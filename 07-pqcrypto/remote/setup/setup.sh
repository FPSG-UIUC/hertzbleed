#!/bin/bash
../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT $1 1000 400 bit_recovered.txt
../../PQCrypto-SIDH/sike751/test_SIKE_CLIENT $1 1000 4000 bit_recovered.txt >> $1.txt

