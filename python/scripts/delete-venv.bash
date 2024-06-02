#!/bin/bash
readonly VENV="venv"

if [ ! -e "setup.py" ]; then
    echo "Current directory does not appear to be a python package..."
    echo
    exit 1
fi

if [ -d "$VENV" ]; then
    rm -rf "$VENV"
fi
