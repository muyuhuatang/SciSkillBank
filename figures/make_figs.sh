#!/bin/sh
# Regenerate every figure in this bundle. No network, no GPU, no API calls.
set -e
cd "$(dirname "$0")"
python3 fig4_measurement_instability.py
echo "done: fig4_measurement_instability.pdf"
