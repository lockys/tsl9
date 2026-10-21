#!/bin/sh
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$here/../../.." && pwd)
if [ "$#" -eq 0 ]; then
    exec "${PYTHON:-python3}" -B "$here/check.py" --project-root "$root"
fi
exec "${PYTHON:-python3}" -B "$here/review.py" "$@"
