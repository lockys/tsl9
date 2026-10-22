#!/bin/sh
set -eu
exec "${PYTHON:-python3}" -B "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/check-source.py" "$@"
