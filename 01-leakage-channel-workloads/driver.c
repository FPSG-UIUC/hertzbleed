#include <sys/resource.h>

#include "../util/freq-utils.h"
#include "../util/msr-utils.h"
#include "../util/rapl-utils.h"
#include "../util/util.h"

volatile static int attacker_core_ID;

#define TIME_BETWEEN_MEASUREMENTS 5000000L // 5 millisecond

// Runs the given command
static void stress(void *command)
{
	system((char *)command);
}

struct args_t {
	uint64_t iters;
	char *selector;
};

// Collects traces
static __attribute__((noinline)) int monitor(void *in)
{
	static int rept_index = 0;

	struct args_t *arg = (struct args_t *)in;

	// Pin monitor to a single CPU
	pin_cpu(attacker_core_ID);

	// Set filename
	char energy_filename[64];
	sprintf(energy_filename, "./out/energy_%s_%06d.out", arg->selector, rept_index);
	char freq_filename[64];
	sprintf(freq_filename, "./out/freq_%s_%06d.out", arg->selector, rept_index);
	rept_index += 1;

	// Prepare output file
	FILE *energy_file = fopen((char *)energy_filename, "w");
	if (energy_file == NULL) {
		perror("output file");
	}
	FILE *freq_file = fopen((char *)freq_filename, "w");
	if (freq_file == NULL) {
		perror("output file");
	}

	// Prepare
	double energy, prev_energy = rapl_msr(attacker_core_ID, PKG_ENERGY);
	struct freq_sample_t freq_sample, prev_freq_sample = frequency_msr_raw(attacker_core_ID);
	// uint32_t freq = frequency_cpufreq(attacker_core_ID);

	// Collect measurements
	for (uint64_t i = 0; i < arg->iters; i++) {

		// Wait before next measurement
		nanosleep((const struct timespec[]){{0, TIME_BETWEEN_MEASUREMENTS}}, NULL);

		// Collect measurement
		freq_sample = frequency_msr_raw(attacker_core_ID);
		// uint32_t khz = frequency_cpufreq(attacker_core_ID);

		energy = rapl_msr(attacker_core_ID, PKG_ENERGY);
		fprintf(energy_file, "%.15f\n", energy - prev_energy);
		prev_energy = energy;

		// Store measurement
		uint64_t aperf_delta = freq_sample.aperf - prev_freq_sample.aperf;
		uint64_t mperf_delta = freq_sample.mperf - prev_freq_sample.mperf;
		uint32_t khz = (maximum_frequency * aperf_delta) / mperf_delta;
		fprintf(freq_file, "%" PRIu32 "\n", khz);

		// Save current
		prev_freq_sample = freq_sample;
	}

	// Clean up
	fclose(energy_file);
	fclose(freq_file);
	return 0;
}

int main(int argc, char *argv[])
{
	// Check arguments
	if (argc != 4) {
		fprintf(stderr, "Wrong Input! Enter: %s <ntasks> <samples> <outer>\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// Read in args
	int ntasks;
	struct args_t arg;
	int outer;
	sscanf(argv[1], "%d", &ntasks);
	if (ntasks < 0) {
		fprintf(stderr, "ntasks cannot be negative!\n");
		exit(1);
	}
	sscanf(argv[2], "%" PRIu64, &(arg.iters));
	sscanf(argv[3], "%d", &outer);
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
	char *selectors[100];
	size_t len = 0;
	ssize_t read = 0;
	char *line = NULL;
	while ((read = getline(&line, &len, selectors_file)) != -1) {
		if (line[read - 1] == '\n')
			line[--read] = '\0';

		// Read selector
		selectors[num_selectors] = strdup(line);
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
	rapl_msr(attacker_core_ID, PKG_ENERGY);

	// Run experiment once for each selector
	for (int i = 0; i < outer * num_selectors; i++) {

		// Set alternating selector
		arg.selector = selectors[i % num_selectors];

		// Prepare for experiments
		pthread_t thread1, thread2;

		// Prepare background stress command
		char cpu_mask[16], command[256];
		sprintf(cpu_mask, "0-%d", ntasks - 1);
		sprintf(command, "taskset -c %s stress-ng -q --cpu %d --cpu-method %s -t 10m", cpu_mask, ntasks, selectors[i % num_selectors]);
		printf("Running: %s\n", command);

		// Cool down
		sleep(90);

		// Start stress
		pthread_create(&thread1, NULL, (void *)&stress, (void *)command);

		// Start monitor
		pthread_create(&thread2, NULL, (void *)&monitor, (void *)&arg);

		// Wait for monitor to be done
		pthread_join(thread2, NULL);

		// Stop stress
		system("pkill -f stress-ng");

		// Join stress
		pthread_join(thread1, NULL);
	}
}
