#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

# shellcheck disable=SC1091
source "$DIR/functions.bash"

# Load name and version from the project manifest
VERSION="$(get_project_version)"
readonly VERSION

PROJECT_NAME="$(get_project_name)"
readonly PROJECT_NAME

# Waits for an index to serve the version, then installs it once.
#
# A freshly uploaded release takes time to appear on the index that just accepted it, so
# something has to wait. 'rt net::await_url' backs off across about 7.75 minutes and
# returns as soon as the version is there, instead of a fixed sleep that either wastes
# time or fails a publish that worked.
#
# curl rather than a retried 'uv pip install', which is what this replaced: uv caches
# index responses, negative answers included, so a retried install re-reads the cached
# "no such version" in about 2ms and the whole ladder expires without asking the index
# again. '--refresh-package' on the install below is the other half of that, and it was
# missing here.
await_index() {
    rt net::await_url "$1/pypi/$PROJECT_NAME/$VERSION/json"
}

if [[ "$#" -eq 0 ]]; then
    echo "You must specify --test or --prod as arguments" >&2
    echo
    exit 1
fi

echo "Creating a virtual env..."
VENV="$(mktemp -d)/venv"
readonly VENV
# '--no-project' keeps the env detached from the working tree, so the check
# really does exercise the published artifact rather than the local source.
uv venv --no-project "$VENV"
# 'uv pip' targets this env instead of the project's .venv
export VIRTUAL_ENV="$VENV"

echo "Copying verification script..."
cp "$DIR"/../src/scripts/verify_install.py "$VENV/verify_install.py"

echo "Attempting to install version ($VERSION) in virtualenv ($VENV)..."
while [[ "$#" -gt 0 ]]; do
    case $1 in
    --test)
        # The cli extras come from the main index because test.pypi does not
        # carry every third-party package.
        CLI_DEPS="$(uv run --no-project python -c "import tomllib; print(' '.join(tomllib.load(open('$DIR/../pyproject.toml','rb'))['project'].get('optional-dependencies', {}).get('cli', [])))")"
        if [ -n "$CLI_DEPS" ]; then
            echo "Installing cli extras from main index, since not all packages are available in test.pypi..."
            # shellcheck disable=SC2086
            uv pip install $CLI_DEPS
        fi
        await_index "https://test.pypi.org"
        echo "Attempting install: ${PROJECT_NAME}==$VERSION"
        uv pip install --refresh-package "$PROJECT_NAME" --index-url https://test.pypi.org/simple/ "${PROJECT_NAME}==$VERSION"
        ;;
    --prod)
        await_index "https://pypi.org"
        echo "Attempting install: ${PROJECT_NAME}==$VERSION"
        uv pip install --refresh-package "$PROJECT_NAME" "${PROJECT_NAME}[cli]==$VERSION"
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
"$VENV/bin/python" verify_install.py
popd >/dev/null 2>&1

echo "Virtualenv location: $VENV"
