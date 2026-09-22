#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
TARGET="${1:-.}"

exec python3 "$SCRIPT_DIR/ai_tooling.py" verify "$TARGET"
