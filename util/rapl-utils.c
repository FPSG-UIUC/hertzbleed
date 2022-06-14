/* Inspired by http://web.eece.maine.edu/~vweaver/projects/rapl/rapl-read.c */

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "msr-utils.h"
#include "rapl-utils.h"

#define MSR_RAPL_POWER_UNIT 0x606

/* Package RAPL Domain */
#define MSR_PKG_RAPL_POWER_LIMIT 0x610
#define MSR_PKG_ENERGY_STATUS 0x611
#define MSR_PKG_PERF_STATUS 0x613
#define MSR_PKG_POWER_INFO 0x614

/* PP0 RAPL Domain */
#define MSR_PP0_POWER_LIMIT 0x638
#define MSR_PP0_ENERGY_STATUS 0x639
#define MSR_PP0_POLICY 0x63A
#define MSR_PP0_PERF_STATUS 0x63B

/* PP1 RAPL Domain, may reflect to uncore devices */
#define MSR_PP1_POWER_LIMIT 0x640
#define MSR_PP1_ENERGY_STATUS 0x641
#define MSR_PP1_POLICY 0x642

/* DRAM RAPL Domain */
#define MSR_DRAM_POWER_LIMIT 0x618
#define MSR_DRAM_ENERGY_STATUS 0x619
#define MSR_DRAM_PERF_STATUS 0x61B
#define MSR_DRAM_POWER_INFO 0x61C

/* PSYS RAPL Domain */
#define MSR_PLATFORM_ENERGY_STATUS 0x64d

static double cpu_energy_unit, dram_energy_unit;

/*
 * Needs to be called before calling rapl_msr
 * TODO: needs to be adjusted to work on different CPUs
 */
int set_rapl_units(int core_ID)
{
	long long result;

	result = my_rdmsr_on_cpu(core_ID, MSR_RAPL_POWER_UNIT);
	cpu_energy_unit = pow(0.5, (double)((result >> 8) & 0x1f));

	// FIXME: Change this code to detect CPU family
	// On Haswell EP and Knights Landing the DRAM units
	// differ from the CPU ones.
	if (0) {
		dram_energy_unit = pow(0.5, (double)16);
	} else {
		dram_energy_unit = cpu_energy_unit;
	}

	return 0;
}

/*
 * Types:
 *     0 = MSR_PKG_ENERGY_STATUS
 *     1 = MSR_PP0_ENERGY_STATUS
 *     2 = MSR_PP1_ENERGY_STATUS
 *     3 = MSR_DRAM_ENERGY_STATUS
 *     4 = MSR_PLATFORM_ENERGY_STATUS
 */
double rapl_msr(int core_ID, int type)
{
	double power = 0;
	long long result;

	// Package Energy
	if (type == PKG_ENERGY) {
		result = my_rdmsr_on_cpu(core_ID, MSR_PKG_ENERGY_STATUS);
		power = (double)result * cpu_energy_unit;
	}

	// PP0 energy
	// Not available on Knights*
	// Always returns zero on Haswell-EP?
	if (type == PP0_ENERGY) {
		result = my_rdmsr_on_cpu(core_ID, MSR_PP0_ENERGY_STATUS);
		power = (double)result * cpu_energy_unit;
	}

	// PP1 energy
	// not available on *Bridge-EP
	if (type == PP1_ENERGY) {
		result = my_rdmsr_on_cpu(core_ID, MSR_PP1_ENERGY_STATUS);
		power = (double)result * cpu_energy_unit;
	}

	// Updated documentation (but not the Vol3B) says Haswell and
	// Broadwell have DRAM support too
	if (type == DRAM_ENERGY) {
		result = my_rdmsr_on_cpu(core_ID, MSR_DRAM_ENERGY_STATUS);
		power = (double)result * dram_energy_unit;
	}

	// Skylake and newer for Psys
	if (type == PLATFORM_ENERGY) {
		result = my_rdmsr_on_cpu(core_ID, MSR_PLATFORM_ENERGY_STATUS);
		power = (double)result * cpu_energy_unit;
	}

	return power;
}
