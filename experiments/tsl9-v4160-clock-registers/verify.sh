#!/bin/sh
set -eu
model_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_bin=${PYTHON:-python3}
exec "$python_bin" -B "$model_dir/verify.py" "$@"
