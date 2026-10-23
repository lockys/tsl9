# Feature dispatcher: offline validation record

[繁體中文](README.md)

Three [C/C++ units](../../src/readme.en.md) reconstruct 14D2E–154A6, the 829E getter and two relative tables. Data-only relocation at recorded original addresses matches all 1922 code bytes and 60 table bytes against the official BIN. The joined graph contains 5088 code bytes and 60 table bytes, with 70 direct undefined symbols plus indirect dependencies. It is not flashable firmware.

See the [summary](summary.json), [callback frontier](callback-frontier.json), [limited review status](independent-review.json) and [recipes and limits](../../experiments/tsl9-feature-dispatch/readme.en.md). Current normal C11/C++17 artifacts pass. New rejection checks have no new negative-case matrix; the independent review continuation was stopped by a safety check and was not retried or rerouted.

Of ten public receipts, seven retain exact original bytes. Three replace paths only and are explicitly marked as derivatives. [Provenance](publication-provenance.json) records original/public hashes, sizes and reversible whole-JSON equality. Original receipts and a verified 781-file archive remain local. Anonymous copies are not original replay inputs.

```sh
python3 scripts/check-feature-dispatch-publication.py
```

This read-only check requires the retained local originals. No network, hardware operation or target execution occurred.
