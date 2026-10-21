#!/bin/sh
set -eu
model_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" "$model_dir/verify.py" "$@"
