/* Inspired by the functions aperfmperf_snapshot_khz and arch_freq_get_on_cpu in
https://github.com/torvalds/linux/blob/master/arch/x86/kernel/cpu/aperfmperf.c */

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <unistd.h>

#include "freq-utils.h"
#include "msr-utils.h"

#define MSR_IA32_MPERF 0x000000e7
#define MSR_IA32_APERF 0x000000e8
#define MSR_PLATFORM_INFO 0x000000ce

// This is CPU-specific
unsigned int maximum_frequency;

/*
 * Needs to be called before calling frequency_msr.
 * See Intel SDM for information, or also see here:
 * https://stackoverflow.com/a/16271541/5192980
 */
int set_frequency_units(int core_ID)
{
	maximum_frequency = ((my_rdmsr_on_cpu(core_ID, MSR_PLATFORM_INFO) >> 8) & 0xFF) * 100000;
	// printf("Maximum frequency %u\n", maximum_frequency);
	return 0;
}

/*
 * Returns the raw aperf and mperf values (not the frequency)
 * See function below to learn how to use these values
 */
struct freq_sample_t frequency_msr_raw(int core_ID)
{
	struct freq_sample_t freq_sample;
	freq_sample.aperf = my_rdmsr_on_cpu(core_ID, MSR_IA32_APERF);
	freq_sample.mperf = my_rdmsr_on_cpu(core_ID, MSR_IA32_MPERF);
	return freq_sample;
}

/*
 * Returns the frequency measured just like cpufreq does in the kernel
 *     https://lkml.org/lkml/2016/4/1/7
 *     https://github.com/torvalds/linux/blob/master/arch/x86/kernel/cpu/aperfmperf.c
 */
uint32_t frequency_msr(int core_ID)
{
	uint64_t aperf_1, aperf_2, aperf_delta;
	uint64_t mperf_1, mperf_2, mperf_delta;

	aperf_1 = my_rdmsr_on_cpu(core_ID, MSR_IA32_APERF);
	mperf_1 = my_rdmsr_on_cpu(core_ID, MSR_IA32_MPERF);

	// Sleep 10 milliseconds
	nanosleep((const struct timespec[]){{0, 10000000L}}, NULL);

	aperf_2 = my_rdmsr_on_cpu(core_ID, MSR_IA32_APERF);
	mperf_2 = my_rdmsr_on_cpu(core_ID, MSR_IA32_MPERF);

	aperf_delta = aperf_2 - aperf_1;
	mperf_delta = mperf_2 - mperf_1;

	return (maximum_frequency * aperf_delta) / mperf_delta;
}

/*
 * Gets the current CPU frequency from scaling_cur_freq (easier than the MSR)
 */
uint32_t frequency_cpufreq(int cpu_id)
{
	// Open sysfs CPU frequency file once
	static FILE *cur_freq_file = NULL;
	if (!cur_freq_file) {
		char file_name[100];

		// scaling_cur_freq is the file with the current frequency on our system
		sprintf(file_name, "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_cur_freq", cpu_id);

		cur_freq_file = fopen(file_name, "r");
		if (cur_freq_file == NULL) {
			perror("Error opening scaling_cur_freq file");
			exit(1);
		}
	}

	// Read current CPU frequency
	uint32_t scaling_cur_freq = 0;
	if (cur_freq_file) {
		rewind(cur_freq_file);
		fflush(cur_freq_file);
		if (fscanf(cur_freq_file, "%" PRIu32, &scaling_cur_freq) == 1) {
			return scaling_cur_freq;
		}
	}

	// Abort if file could not be opened or read
	fprintf(stderr, "Unable to get cpufreq\n");
	fclose(cur_freq_file);
	cur_freq_file = NULL;
	return -1;
}
