#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

VENV="$(mktemp -d)"
VERSION="$(cat "$DIR"/../../VERSION)"
echo "Attempting to install version ($VERSION) in virtualenv ($VENV)..."

python -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --index-url https://test.pypi.org/project "jazzy_fish==$VERSION"
