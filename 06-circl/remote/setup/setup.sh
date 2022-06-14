#!/bin/bash

../../circl/dh/sidh/POC_ATTACK/sike_client 300 400 bit_recovered.txt $1
../../circl/dh/sidh/POC_ATTACK/sike_client 300 4000 bit_recovered.txt $1 >> $1.txt

