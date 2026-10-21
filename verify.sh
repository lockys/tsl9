#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" "$root/scripts/portable_verify.py" "$@"
fi
for executable in python3 python; do
    if command -v "$executable" >/dev/null 2>&1 && "$executable" -c 'import sys; sys.exit(sys.version_info < (3,10))' >/dev/null 2>&1; then
        exec "$executable" "$root/scripts/portable_verify.py" "$@"
    fi
done
echo 'Python 3.10+ is required. Set PYTHON to its executable path.' >&2
exit 1
