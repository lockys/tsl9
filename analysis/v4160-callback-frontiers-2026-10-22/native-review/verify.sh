#!/bin/sh
set -eu
scope_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
    exec python3 -B "$scope_dir/check.py" "$@"
fi
exec python -B "$scope_dir/check.py" "$@"
