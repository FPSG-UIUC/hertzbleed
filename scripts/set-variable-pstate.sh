#!/usr/bin/env bash

# Disable Turboboost (optional)
echo "0" | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo