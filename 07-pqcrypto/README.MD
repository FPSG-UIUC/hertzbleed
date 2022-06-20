# Attack on Microsoft PQCrypto-SIDH

We used these scripts for the local attack (Figure 9b in the paper) and the remote attack (Figure 10b and 12 in the paper) against PQCrypto-SIDH.

## Preliminaries
1. Clone and patch the official `PQCrypto-SIDH` repository:

```sh
git clone git@github.com:microsoft/PQCrypto-SIDH.git
cd PQCrypto-SIDH
git reset --hard effa607f244768cdd38f930887076373604eaa78
patch -p1 < ../pqc.patch
```
Build PQCrypto-SIDH as suggested by the README

2. Compile the monitor for the local POC:
```sh
cd ../local
make
```

## Local POC: Explanation
<!-- Files we modified: src/ec_isogeny.c src/sike.c 
	src/p751/p751.c src/p751/P751_compressed.c 
	src/p610/p610.c src/p610/P610_compressed.c
	src/p503/p503.c src/p503/P503_compressed.c
	src/p434/p434.c src/p434/P434_compressed.c
	tests/local.c tests/client.c tests/server.c tests/test_SIKEp751_LOCAL.c 
      	MAKEFILE
      	
All code we added start with comment //Code from Author -->

After build PQCrypto-SIDH, the executable for local attack is `sike751/test_SIKE_LOCAL`

The purpose of the local POC is to demonstrate that the power consumption and CPU frequency during SIKE's decapsulation algorithm can depend on single bits of the secret key. Assume we target bit `i` of a certain secret key `m`. As we saw in our paper, if `m[i] != m[i-1]`, we expect the power consumption to be lower and the CPU frequency to be higher during decapsulation.


In the local POC we use `test_SIKE_LOCAL` as the victim.
This `test_SIKE_LOCAL` features 10 hardcoded randomly generated secret keys. It takes in 6 parameters: 

1. `flip_key`: Do we flip the bit at `target_bit` for this key? Recall that power consumption and frequency depend on the xor of bit at [`target_bit`] and bit at [`target_bit`-1].
2. `key_index`: the secret key we use for this run (out of the 10 keys).
3. `target_bit`: the target bit index for this POC attack.
4. `number_thread`: the number of pthreads doing decapsulation start simultaneously for one iteration.
5. `iteration`: the number of iterations.
6. `amplification`: There are 2 types of decapsulation function: 
    1. The original one: `crypto_kem_dec`, which should pass in 0 for amplification
    2. The amplified one: `crypto_kem_dec_amplification`: For Hertzbleed amplification. The function that generates anomalous 0 is `EphemeralSecretAgreement_B`. We can remove all the function after EphemeralSecretAgreement_B and loop it for "amplification" iterations to see a better result of Hertzbleed. To invoke this function, just pass in any non zero value for amplification. 


In our local POC script, we target 2 random position for each 10 secret key, and we monitor the CPU frequency and power consumption while `test_SIKE_LOCAL` runs the respective decapsulations.




## Local POC: Collect traces

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
Then, to reproduce the results of the paper, run the following script from the `07-pqcrypto/local` directory:
```sh
cd 07-pqcrypto/local
./run-local.sh
```
The script will take about 10 hours to finish.


## Local POC: Plot traces
To plot the traces collected above, depending on the setup you chose, run any of the following (with the correct `${date}`).

For Figure 9b:
```sh
cd 07-pqcrypto/local
python ./plot-local.py --freq --hist data/out-${date}
python ./plot-local.py --energy --hist data/out-${date}
```

The scripts should produce figures similar to the ones in the paper, and store them in the `plot` subfolder.
You might need to manually change the FIXMEs in plot-local for excluding outliers in frequency and energy data.


## Local POC: Variant

We also include a variant of the above POC where we measure the decapsulation time instead of monitoring frequency and power consumption. 
These results are not in the paper. 
To run this variant POC, run the following script from the `07-pqcrypto` directory:

```sh
cd 07-pqcrypto/local
./run-local-time.sh >> output.txt
```

To plot the results, use:

```sh
python ./plot-local-time.py output.txt 
```

The purpose of this POC is to demonstrate that differences in the CPU frequency during SIKE's decapsulation algorithm translate to differences in execution time. Assume we target bit `i` of a certain secret key `m`. As we saw in our paper, if `m[i] != m[i-1]`, we expect the runtime of the decapsulation to be lower.

## Remote attack: Explanation

The purpose of the remote POC is to demonstrate that: execution time of SIKE key decapsulation (PQCrypto-SIDH) can be secret key dependent and observed remotely if running on machine vulnerable to Hertzbleed. Recall from our paper: Assuming we target `i` of a certain secret key `m`, energy will decrease and frequency will increase if the `m[i]` not equal to `m[i-1]`, in which case we expect to see a performance speedup; otherwise, we should not see a performance speedup.


After build PQCrypto-SIDH, the executables are in `sike751/test_SIKE_CLIENT`, `sike751/test_SIKE_SERVER`

Our `tests/test_SIKE_SERVER.c` generates a random secret key and the corresponding public key, it accepts the following requests:
   1. takes in a ciphertext and decapsulates it. 
   2. takes in a SECRET command and output the secret. (We provide this command for your convenience)
   3. takes in a PUB command and send back the public key.


Our `tests/test_SIKE_CLIENT.c` can send decapsulation requests to the server and it takes in 4 parameters:
   1. `target_bit`: the index of the bit we target for this attack.
   2. `connection`: the number of requests we want to start simultaneously.
   3. `iteration`: the number of iterations we want to run for this attack.
   4. `filename`: the file contains the already recovered key. The format of this file should be: one bit a line with no extra information.
    
`test_SIKE_CLIENT`:
   1. Every time we run the `test_SIKE_CLIENT`, it will first send PUB command to the server asking for public key.
   2. If `connection==0`, the `test_SIKE_CLIENT` will send the SECRET command to the server asking it to reveal the secret.
   3. If `iteration==0`, The `test_SIKE_CLIENT` discovered enough bits of secret key and decided to bruteforce the rest of the unrecovered secret key bits by confirming with the public key. We recommend you to start bruteforcing after extracting ~365 number of secret key bits. After extracting the full secret key, the `test_SIKE_CLIENT` will confirm the recovered secret key by sending the SECRET command to the server asking it to reveal the secret.
   4. Otherwise, it will send `connection` number of requests and print the total response time. Repeat the attack for `iteration`.
   
   
## Remote attack: Attack Setup 
Client side:
```sh
cd 07-pqcrypto/remote/setup/
```

To successfully launch the attack, we need to set two thresholds for time(`m[i]` == `m[i-1]`) and time(`m[i]` != `m[i-1]`) so that we can distinguish this two cases and do the attack.


   1. Server side: Start the server. 
```sh
cd 07-pqcrypto
./sike751/test_SIKE_SERVER
```
   Server will send public key to the client once client connects.
  
   2. Client side: Change the IP of the server in the `tests/client.c` file: line 131, 28. It is 130.126.136.241 by default. Recompile after IP modified.

   3. We determine time(`m[i]` == `m[i-1]`).
   When `m[i]` == `m[i-1]`, anomalous 0s are not triggered, we should see no speedup. The decapsulation times of the challenge ciphertext are indistinguishable from the ones of a random ciphertext. We query the server with random ciphertext and determine the cutoff for time(`m[i]` == `m[i-1]`). `bit_recovered_nospeedup.txt` contains a randomly secret key that hopefully is not the same as your target. 

   ```sh	
   ./setup_nospeedup.sh
   ```
   We assume connection = 1000, iteration = 400. If the parameters does not work well for you, you can change them in the scripts:

   ```sh
   rm setup_nospeedup.sh
   python bench-setup.py connection iteration >> setup_nospeedup.sh
   chmod u+x setup_nospeedup.sh
   ```

   `setup_nospeedup.sh` collects 20000 data points for time(`m[i]` == `m[i-1]`) and will be saved in the `output_nospeedup.txt`

   4. We next determine time(`m[i]` != `m[i-1]`). 
   Any randomly generated secret key will likely have `m[i]` != `m[i-1]` in the top bits. The secret key is assumed to have 0 at index -1. We can start from index 0 and probe the server with ciphertext described in the paper. If we receive a timing distribution similar to that we got in step 3, we claim `m[i]` == `m[i-1]`. If we receive a timing distribution with a significant left shift compare to that we got in step 3, we claim `m[i]` != `m[i-1]`. You should decide yourself if it is a significant left shift. If we do not see a speedup at index 0, we claim `m[0] = 0`, and proceed to next bit. Specifically:
   ```sh	
   touch bit_recovered.txt
   for i in [0...50]:
      ./setup.sh i
      python compare.py output_nospeedup.txt i.txt low high
      if observe leftshift:
         echo 1 >> bit_recovered.txt
         break
      echo 0 >> bit_recovered.txt
   ```
   We assume connection = 1000, iteration = 4000. If the parameters does not work well for you, you can change them in the `setup.sh`.

   `compare.py` will output a graph `attack_compare.jpeg` plotting the two distributions: one from `output_nospeedup.txt` and one from `i.txt`. 
   `low` and `high` need to be determined experimentally. They are used as filters to exclude outliers.

   Once we find an `i` produces a left shift, it means that we encounters `m[i]` != `m[i-1]`. We should break here. `compare.py` will output `unknown mean` which is the time(`m[i]` != `m[i-1]`), `no speedup mean` which is the time(`m[i]` == `m[i-1]`). Save `i` as `starting_index` for attack below. 
   

## Remote attack: Attack
Client side:
```sh
cd 07-pqcrypto/remote/attack/
cp ../setup/bit_recovered.txt ./
```
   1. Now we time(`m[i]` == `m[i-1]`) and time(`m[i]` != `m[i-1]`). We can proceed the attack with less `iterations`:
   Create a folder called `remote_result`.

```sh
mkdir remote_result
for i in `seq 0 starting_index`; do	
   cp ../setup/${i}.txt ./remote_result/
done
``` 

   2. In `data.py`, modify low and high as determined in step 4 above. low and high are for excluding outliers.

   3. In `data.py`, modify `repeat_high` = (time(`m[i]` == `m[i-1]`) - `epsilon`), and `repeat_low` = (time(`m[i]` != `m[i-1]`) + `epsilon`). (`repeat_low`, `repeat_high`) are for thresholding. If the median of iterations falls into (`repeat_low`, `repeat_high`) we want to repeat the experiment because the result is inconclusive. If the median is below `repeat_low`, we claim that we see the speedup and `m[i]` != `m[i-1]`. If the median is above `repeat_high`, we claim that we do not see the speedup and `m[i]` == `m[i-1]`. We compute the new bit `m[i]` based on `m[i-1]` and append it to `bit_recovered.txt`. Value of `epsilon` should be tuned empirically. 

    4. Create `attack.sh` and run it.
```sh
python bench.py starting_index+1 connection iteration >> attack.sh
chmod u+x attack.sh
./attack.sh 
```

   5. All results will be in the folder `remote_result`. And after the attack we can compare the recovered key and the real secret key revealed by the server. (If the client outputs backtrack it means that you made a wrong decision in the past bits. Backtrack should be done manually)
   
   6. After the `attack.sh` finishes. Run `plot_paper_figures.py` low high (as determined in profiling) to get (Figure 10b and 12 in the paper)
```sh	
python plot_paper_figures.py low high iteration
```






