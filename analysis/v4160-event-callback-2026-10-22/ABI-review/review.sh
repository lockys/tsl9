#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
runtime=${PYTHON:-python3}
if [ "$#" -eq 0 ]; then
    exec "$runtime" -B "$script_dir/check.py"
fi
exec "$runtime" -B "$script_dir/review.py" "$@"
