#!/bin/sh
set -eu
exec "${PYTHON:-python3}" -B "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/run-effects.py" "$@"
