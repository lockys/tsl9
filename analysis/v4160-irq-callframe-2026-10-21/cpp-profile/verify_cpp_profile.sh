#!/bin/sh
set -eu
script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    python_bin=$PYTHON
elif command -v python3 >/dev/null 2>&1; then
    python_bin=python3
else
    python_bin=python
fi
exec "$python_bin" -X utf8 -B "$script_dir/verify_cpp_profile.py" "$@"
