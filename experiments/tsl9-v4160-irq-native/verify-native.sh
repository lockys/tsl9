#!/bin/sh
set -eu
model_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_root=$(CDPATH= cd -- "$model_dir/../.." && pwd)
scope=v4160-irq-native-2026-10-21/compiler-review
checker="$project_root/analysis/$scope/verify_native.py"
if [ ! -f "$checker" ]; then
    checker="$project_root/apk-analysis/tsl9-$scope/verify_native.py"
fi
exec "${PYTHON:-python3}" "$checker" --project-root "$project_root" "$@"
