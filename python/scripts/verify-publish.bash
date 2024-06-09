#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

if [[ "$#" -eq 0 ]]; then
    echo "You must specify --test or --prod as arguments"
    echo
    exit 1
fi

echo "Creating a virtual env..."
VENV="$(mktemp -d)"
VERSION="$(cat "$DIR"/../../VERSION)"
python -m venv "$VENV"

echo "Copying verification script..."
cp "$DIR"/../src/scripts/verify_install.py "$VENV/verify_install.py"

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "Attempting to install version ($VERSION) in virtualenv ($VENV)..."
while [[ "$#" -gt 0 ]]; do
    case $1 in
    --test)
        pip install --index-url https://test.pypi.org/simple/ "jazzy_fish==$VERSION"
        ;;
    --prod)
        pip install "jazzy_fish==$VERSION"
        ;;
    --*= | -*)
        echo "Error: Unsupported flag $1" >&2
        echo
        exit 1
        ;;
    esac
    shift
done

pushd "$VENV" >/dev/null 2>&1
python verify_install.py
popd >/dev/null 2>&1
