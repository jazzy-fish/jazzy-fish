#!/bin/bash
set -ueo pipefail

echo
echo "Estimates for generating at the 1/ms scale:"
find out/processed -name 'stats*' -exec grep 'Result: ' {} \; | grep '1/ms' | sort

echo
echo "Estimates for generating at the 1/s scale:"
find out/processed -name 'stats*' -exec grep 'Result: ' {} \; | grep '1/s' | sort
