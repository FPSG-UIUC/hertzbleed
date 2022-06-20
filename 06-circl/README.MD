# Attack on Cloudflare CIRCL SIKE

We used these scripts for the local attack (Figure 9a in the paper) and the remote attack (Figure 10a and 11 in the paper) against CIRCL-SIKE.

## Preliminaries

1. Make sure you have golang installed (`sudo apt install -y golang`).
2. Clone and patch the official `circl` repository:
```sh
git clone git@github.com:cloudflare/circl.git
cd circl
git reset --hard 1fc363868f344ff5a071bfc7a6b423a9c22010c9
patch -p1 < ../circl.patch
```
3. Compile the monitor for the local POC:
```sh
cd ../local
make
```
4. Compile the victim for the local POC, and the client and server for the remote POC:
```sh
cd ../circl/dh/sidh/POC_ATTACK
go build -o sike_local sike_local.go
go build -o sike_client sike_client.go
go build -o sike_server sike_server.go
```


## Local POC: Explanation

After build, the executable for the local attack is `circl/dh/sidh/POC_ATTACK/sike_local`.

<!-- Files we modified: dh/sidh/internal/p751/curve.go
dh/sidh/internal/p751/params.go
dh/sidh/POC_ATTACK/sike_client.go
dh/sidh/POC_ATTACK/sike_local.go
dh/sidh/POC_ATTACK/sike_server.go
dh/sidh/sidh.go

        
All code we added start with comment //Code from Yingchen

After build sike_local, the executable for local attack  -->

The purpose of the local POC is to demonstrate that the power consumption and CPU frequency during SIKE's decapsulation algorithm can depend on single bits of the secret key. Assume we target bit `i` of a certain secret key `m`. As we saw in our paper, if `m[i] != m[i-1]`, we expect the power consumption lower and the CPU frequency higher during decapsulation.

In the local POC we use `sike_local` as the victim.
This `sike_local` features 10 hardcoded randomly generated secret keys. It takes in 5 parameters: 
1. `flip_key`: Do we flip the bit at `target_bit` for this key? Recall that power consumption and frequency depend on the xor of `m[target_bit]` and `m[target_bit-1]`.
2. `key_index`: the secret key we use for this run (out of the 10 keys).
3. `target_bit`: the target bit index for this POC attack.
4. `number_thread`: the number of decapsulation goroutines start simultaneously for one iteration.
5. `iteration`: the number of iterations.

In our local POC script, we target 2 random position for each 10 secret key, and we monitor the CPU frequency and power consumption while `sike_local` runs the respective decapsulations.

## Local POC: Collect traces

Make sure that your system is idle and minimize the number of background processes that are running and may add noise to the experiment.
Then, to reproduce the results of the paper, run the following script from the `06-circl/local` directory:
```sh
cd 06-circl/local
./run-local.sh
```
The script will take about 11 hours to finish.

## Local POC: Plot traces
To plot the traces collected above, depending on the setup you chose, run any of the following (with the correct `${date}`).

For Figure 9a:
```sh
cd 06-circl/local
python ./plot-local.py --freq --hist data/out-${date}
python ./plot-local.py --energy --hist data/out-${date}
```
The scripts should produce figures similar to the ones in the paper, and store them in the `plot` subfolder.
You might need to manually change the FIXMEs in plot-local for excluding outliers in frequency and energy data.


## Local POC: Variant

We also include a variant of the above POC where we measure the decapsulation time instead of monitoring frequency and power consumption. 
These results are not in the paper. 
To run this variant POC, run the following script from the `06-circl/local` directory:

```sh
cd 06-circl/local
./run-local-time.sh >> output.txt
```

To plot the results, use:

```sh
cd 06-circl/local
python ./plot-local-time.py output.txt 
```

The purpose of this POC variant is to demonstrate that differences in the CPU frequency during SIKE's decapsulation algorithm translate to differences in execution time. Assume we target bit `m[i]`. As we saw in our paper, if `m[i] != m[i-1]`, we expect the runtime of the decapsulation to be lower. 



## Remote attack: Explanation
The purpose of the remote POC is to demonstrate that: execution time of SIKE key decapsulation (CIRCL) can be secret key dependent and observed remotely if running on machine vulnerable to Hertzbleed. Recall from our paper: Assuming we target `i` of a certain secret key `m`, energy will decrease and frequency will increase if the `m[i]` not equal to `m[i-1]`, in which case we expect to see a performance speedup; otherwise, we should not see a performance speedup.


`sike_client` and `sike_server` are the executables for this attack

Our `sike_server.go` generates a random secret key and the corresponding public key (print it), it accepts the following requests:
   1. takes in a ciphertext and decapsulates it. 
   2. takes in a SECRET command and output the secret. (We provide this command for your convenience)
   3. takes in a SHUT command, outputs the secret and closes the server.


Our `sike_client.go` can send decapsulation requests to the server and it takes in 4 parameters:
   1. `request_count`: the number of requests start simultaneously.
   2. `iterations`: the number of iterations run for this attack.
   3. `filename`: the file contains the already recovered key. The format of this file should be: one bit a line with no extra information.
   4. `index_to_recover`: the index of the bit to target for this attack.
    
`sike_client`:
   1. If `request_count`==0, the sike_client will send the SECRET command to the server asking it to reveal the secret.
   2. If `iterations`==0, The `sike_client` should already have discovered enough bits of secret key and decided to bruteforce the rest of the unrecovered secret key bits by confirming with the public key. We recommend you to start bruteforcing after extracting ~365 number of secret key bits. After extracting the full secret key, the `sike_client` will confirm the recovered secret key by sending the SHUT command to the server asking it to reveal the secret and terminate itself.
   3. Otherwise, it will send `request_count` number of requests and print the total response time. Repeat the attack for `iterations`.


## Remote attack: Attack Setup 
Client side:
```sh
cd 06-circl/remote/setup/
```

To successfully launch the attack, we need to set two thresholds for time(`m[i]` == `m[i-1]`) and time(`m[i]` != `m[i-1]`) so that we can distinguish this two cases and do the attack.


   
   1. Server side: Start the server. 
```sh
cd 06-circl
./circl/dh/sidh/POC_ATTACK/sike_server
```
   Server will output the public key.
   `sike_client.go` should know the public key of the server. The public key in `sike_client.go` is hardcoded. After `sike_server` outputs the public key in hex format, it should be manually copied to the client side. The server output the public key as the following order: `public_key_server_pt0[A], public_key_server_pt0[B], public_key_server_pt1[A], public_key_server_pt1[B], public_key_server_pt2[A], public_key_server_pt2[B]`. And client should be recompiled.


   2. Change the IP of the server in the `sike_client.go` file: line 37. It is 130.126.136.241 by default. Recompile the `sike_client.go` after IP modified.


   3. We determine time(`m[i]` == `m[i-1]`).
   When `m[i]` == `m[i-1]`, anomalous 0s are not triggered, we should see no speedup. The decapsulation times of the challenge ciphertext are indistinguishable from the ones of a random ciphertext. We query the server with random ciphertext and determine the cutoff for time(`m[i]` == `m[i-1]`). `bit_recovered_nospeedup.txt` contains a randomly secret key that hopefully is not the same as your target. 

   ```sh	
   ./setup_nospeedup.sh
   ```
   We assume connection = 300, iteration = 400. If the parameters does not work well for you, you can change them in the scripts:

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
   We assume connection = 300, iteration = 4000. If the parameters does not work well for you, you can change them in the `setup.sh`.

   `compare.py` will output a graph `attack_compare.jpeg` plotting the two distributions: one from `output_nospeedup.txt` and one from `i.txt`. 
   `low` and `high` need to be determined experimentally. They are used as filters to exclude outliers.

   Once we find an `i` produces a left shift, it means that we encounters `m[i]` != `m[i-1]`. We should break here. `compare.py` will output `unknown mean` which is the time(`m[i]` != `m[i-1]`), `no speedup mean` which is the time(`m[i]` == `m[i-1]`). Save `i` as `starting_index` for attack below. 


## Remote attack: Attack
Client side:
```sh
cd 06-circl/remote/attack/
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
   
   6. After the `attack.sh` finishes. Run `plot_paper_figures.py` low high (as determined in profiling) to get (Figure 10a and 11 in the paper)
```sh	
python plot_paper_figures.py low high iteration
```


