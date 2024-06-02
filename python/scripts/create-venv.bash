#!/bin/bash
readonly VENV="venv"

if [ ! -e "setup.py" ]; then
    echo "Current directory does not appear to be a python package..."
    echo
    exit 1
fi

rm -rf "$VENV"
python -m venv "$VENV"

# shellcheck disable=SC1091
source "$VENV"/bin/activate

pip install -r requirements.txt
pip install -e .
