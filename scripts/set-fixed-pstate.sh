#!/usr/bin/env bash

# Disable Turboboost (optional)
echo "1" | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo