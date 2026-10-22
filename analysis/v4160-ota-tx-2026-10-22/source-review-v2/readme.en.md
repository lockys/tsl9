# TX raw source proof: JSON shape correction

[繁體中文](readme.zh-TW.md)

This narrowly supersedes the public checker in the immutable sibling `source-review`, seal `46da5762a0bc46c15a04ad6b2bf0f890a001de66b8ac006d0c507529505d76e2`. Its eleven files, raw decoder, 280-byte/96-instruction proof, forty operand controls, contracts and retained evidence remain unchanged. The old checker fails because fresh basic-block extents contain Python tuples while JSON readback contains lists. This was a checker serialization comparison defect, not a newly discovered instruction or contract change.

The new checker verifies every old sealed file, invokes the original proof, and JSON-normalizes the freshly computed values before exact comparison. Five structural controls reject changed tuple/list endpoints, reversed or missing extents and wrong arity. Shape normalization accepts no value changes. The original mismatched direct comparison is deliberately reproduced as a diagnostic. No reconstructed C/C++ or target code is executed.

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/source-review-v2/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

The `.sh` wrapper accepts the same arguments and `PYTHON` override. An optional repeated `--object ACTUAL_CARRIER.o` additionally rereads that actual carrier's symbols, relocations and raw body. Default output reports zero actual archived carrier replays; retained historical carrier metadata is never presented as a fresh replay. The selected preseal actual check independently reread the original carrier and current twelve-function carrier. The source proof still cannot establish computed-reference absence, opaque ROM behavior, hardware operation or OTA readiness. New C/C++ HOST review is a separate scope.
