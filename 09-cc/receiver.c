#include "../util/util.h"
#include "../util/freq-utils.h"

int main(int argc, char *argv[])
{
	uint64_t i;

	// Check arguments
	if (argc != 2) {
		fprintf(stderr, "Wrong Input! channel interval!\n");
		fprintf(stderr, "Enter: %s <interval>\n", argv[0]);
		exit(1);
	}

	// Prepare output filename
	FILE *output_file = fopen("./out/receiver-contention.out", "w");

	// Parse channel interval
	uint64_t interval = 1; // C does not like this if not initialized
	sscanf(argv[1], "%" PRIu64, &interval);
	if (interval <= 0) {
		printf("Wrong interval! interval should be greater than 0!\n");
		exit(1);
	}

	// Prepare samples array
	const uint64_t repetitions = interval / 3000000 * 16100;
	uint64_t *result_x = (uint64_t *)malloc(sizeof(*result_x) * repetitions);
	uint32_t *result_y = (uint32_t *)malloc(sizeof(*result_y) * repetitions);

	// Warm Up
	frequency_cpufreq(2);

	// Synchronize
	uint64_t cycles;
	do {
		cycles = get_time();
	} while ((cycles % interval) > 10);

	// Receive
	for (i = 0; i < repetitions; i++) {

		// Wait 1ms before next measurement
		nanosleep((const struct timespec[]){{0, 1000000L}}, NULL);

		// Wait before next measurement
		result_x[i] = get_time();
		result_y[i] = frequency_cpufreq(2);
	}

	// Store the samples to disk
	for (i = 0; i < repetitions; i++) {
		fprintf(output_file, "%" PRIu64 " %" PRIu32 "\n", result_x[i] - result_x[0], result_y[i]);
	}

	// Free the buffers and file
	fclose(output_file);
	free(result_x);
	free(result_y);

	return 0;
}
