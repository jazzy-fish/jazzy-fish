#!/bin/bash
set -ueo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly DIR

# shellcheck disable=SC1091
source "$DIR/functions.bash"

# VERSION="$(cat "$DIR"/../VERSION)"
# readonly VERSION

# Load project name from project manifest
PROJECT_NAME="$(python -c "import toml; print(toml.load('$DIR/../pyproject.toml')['project']['name'])")"
readonly PROJECT_NAME

# Retrieve current git sha
TAG="$(get_git_sha)"
if [ -z "$(is_dirty)" ]; then
    # Working dir is clean, attempt to use tag
    GITTAG="$(get_tag_at_head)"

    # If git tag found, use it
    if [ -n "$GITTAG" ]; then
        TAG="$GITTAG"
    fi
fi

# Build the image
docker build -t "$PROJECT_NAME:$TAG" .
