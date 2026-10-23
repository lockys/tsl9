#!/bin/sh
set -eu
QUEUE_HERE=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
QUEUE_ROOT=$(CDPATH= cd -P "$QUEUE_HERE/../.." && pwd)
exec "${QUEUE_PYTHON:-python3}" "$QUEUE_HERE/check.py" --project-root "$QUEUE_ROOT" "$@"
