"""Check the pinned candidate bytes only; does not compile or test C."""
import hashlib
from pathlib import Path
import sys

candidate = Path(__file__).resolve().parent.parent / "v4160-tx-composed-ram-c" / "candidate.c"
expected = "de88c0b5677d5d036443e022c6ac71b41e7b7de347c184908cc9fc1039d957cf"
actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
if actual != expected:
    sys.exit(f"candidate SHA-256 mismatch: {actual}")
print(f"candidate SHA-256 OK: {actual} (not a C test)")
