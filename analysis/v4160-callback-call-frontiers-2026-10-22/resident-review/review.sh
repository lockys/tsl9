#!/bin/sh
set -eu
scope_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "${PYTHON:-python3}" -B "$scope_dir/review.py" "$@"
