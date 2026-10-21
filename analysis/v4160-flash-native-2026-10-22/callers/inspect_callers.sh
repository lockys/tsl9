#!/bin/sh
set -eu
scope_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" "$scope_dir/inspect_callers.py" "$@"
