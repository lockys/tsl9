# Source-integrated IRQ image inputs

`source-manifest.json` freezes the authoritative original carrier's 691 allocation
metadata records and symbol roles, 34 carrier translation units, 73 original source
and header identities, the 53 canonical section-relative bindings and the reviewed
8270 outside-owned relocation digest. `original-image-layout.ld` is a byte-identical
copy of the historical full 691-section layout (SHA-256 `651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`).

`prepare_manifest.py` documents the one-time provenance extraction from the actual
historical artifacts. It requires that historical archive and is not the fresh
build entry point. Fresh builds need only the published manifest/layout, pinned
startup sources, pinned readable callframe sources/proofs, the original offline
reference image and local LLVM tools. The new runner never links a historical
object or copies its bytes into a failed output section.

Run the separately documented `integration/verify_image.py` in the IRQ image case.
`build/` retains local compiler objects, dependency files, logs, receipts, ELF
witnesses and newly exported images; build archives are excluded from publication.
The five typed functions cover 264 bytes. The rest of the image remains captured
raw carriers; this does not recover the original application's complete C source.
No flashability, physical compatibility, asynchronous equivalence or OTA proof is
claimed.
