#!/bin/sh
set -eu
REA_DELAY_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd)
exec "${PYTHON:-python3}" "$REA_DELAY_DIR/verify.py" "$@"
