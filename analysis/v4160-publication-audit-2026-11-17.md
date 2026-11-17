# v4.1.60 offline publication audit

This is a publication-readiness audit, not a firmware release or an assertion that reverse engineering is complete. The comparison used base commit `eaa3e741ccc9fef8a7f0cd67aac6095c8a01d388` and a local experimental checkpoint `39b21d373614f7dadc261d2af5f504258b52760d`. The checkpoint is not included in this commit.

## Scope and findings

- The checkpoint adds 608 files relative to the base: 376 Python files, 176 Markdown files, 48 C files and 8 JSON files. They include experimental models, test harnesses and reports, not just recovered production C.
- A bounded byte-pattern scan of those files found no matches for selected common GitHub, OpenAI, AWS and Google credential formats or private-key headers. This is not a complete secret, privacy or license audit. It also identified 68 files containing a local user-directory path; these require individual review or redaction before publication.
- One owner-inventory candidate checks a source manifest with SHA-256 `466883524eca536c88653bce14057ec68c8c94d2c56368e185f1c2116abaf739`. The base commit's manifest has SHA-256 `dabc5bfbe07f9d4965d9d2a81eff6d5c015c1e2d377bac7e945fc4d2bd0f843b`. These manifests differ in the recorded hash for `src/native/receive/opaque_allowed_gaps.c`. Consequently, results obtained with the former cannot be treated as reproducible from the base without resolving source provenance and regenerating the evidence.
- On the examined local working snapshot, the owner-inventory test suite passed 7 tests in ordinary Python and 7 with Python `-O`. Those runs used the local manifest and sources; they do not demonstrate a clean-checkout pass on the base. The inventory candidate and its coverage input are not published by this audit.
- Several historic build receipts refer to earlier receipts and artifacts. Some referenced historic paths were absent in the examined temporary copy. UUID-named build directories cannot safely be deleted wholesale merely because they are generated: a later run creates a new receipt, not the original evidence chain.

## Release boundary

Review each candidate's dependencies, provenance, privacy and rights, then run its checks against the exact intended publication tree. Keep unresolved local work and receipt chains intact. Neither this report nor a byte-identical isolated or conditional link establishes physical device behavior, a complete C reconstruction, or a flashable firmware image.
