#include "msr-utils.h"

// Inspired by multiple sources including
//    https://github.com/intel/msr-tools/blob/master/cpuid.c
//    https://github.com/intel/msr-tools/blob/master/rdmsr.c
uint64_t my_rdmsr_on_cpu(int core_ID, int reg)
{
	uint64_t data;
	static int fd = -1;
	static int last_core_ID;

	if (fd < 0 || last_core_ID != core_ID) {
		char msr_filename[BUFSIZ];
		if (fd >= 0)
			close(fd);
		sprintf(msr_filename, "/dev/cpu/%d/msr", core_ID);
		fd = open(msr_filename, O_RDONLY);
		if (fd < 0) {
			if (errno == ENXIO) {
				fprintf(stderr, "rdmsr: No CPU %d\n", core_ID);
				exit(2);
			} else if (errno == EIO) {
				fprintf(stderr, "rdmsr: CPU %d doesn't support MSRs\n", core_ID);
				exit(3);
			} else {
				perror("rdmsr: open");
				exit(127);
			}
		}
		last_core_ID = core_ID;
	}

	if (pread(fd, &data, sizeof data, reg) != sizeof data) {
		if (errno == EIO) {
			fprintf(stderr, "rdmsr: CPU %d cannot read MSR 0x%08" PRIx32 "\n", core_ID, reg);
			exit(4);
		} else {
			perror("rdmsr: pread");
			exit(127);
		}
	}

	return data;
}