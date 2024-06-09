#!/bin/bash
set -euo pipefail
DIR=python

# Create a virtualenv
cd "$DIR"
make create-venv

# Ensure the up-to-date requirements are installed
# shellcheck disable=SC1090
eval "$(make venv)"
make install
