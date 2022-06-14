#ifndef _POWER_CONSUMP_H
#define _POWER_CONSUMP_H

#define PKG_ENERGY 0
#define PP0_ENERGY 1
#define PP1_ENERGY 2
#define DRAM_ENERGY 3
#define PLATFORM_ENERGY 4

int set_rapl_units(int core_ID);
double rapl_msr(int core_ID, int type);

#endif