#ifndef _MY_UTIL_H
#define _MY_UTIL_H

#include <assert.h>
#include <inttypes.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <x86intrin.h>

uint64_t get_time(void);

void pin_cpu(size_t core_ID);

#endif
