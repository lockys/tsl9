#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -P "$(dirname "$0")/../.." && pwd)
exec sh "$root/verify.sh" --model resident-entry "$@"
