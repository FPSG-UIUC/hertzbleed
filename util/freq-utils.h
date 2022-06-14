#ifndef _FREQ_UTILS_H
#define _FREQ_UTILS_H

#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

struct freq_sample_t {
	uint64_t aperf;
	uint64_t mperf;
};

extern unsigned int maximum_frequency;

int set_frequency_units(int core_ID);
struct freq_sample_t frequency_msr_raw(int core_ID);
uint32_t frequency_msr(int core_ID);
uint32_t frequency_cpufreq(int cpu_id);

#endif