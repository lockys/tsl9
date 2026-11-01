# Bounded BOOT and image-shape check

[繁體中文](README.md)

The [checker](check.py) rechecks 15 instruction anchors in the retained ID2580 candidate BOOT and the size of official ID2966 and the TX candidate. Both APP files are 76,800 bytes. Under the previously analyzed BOOT's 1,024-byte page and 0–95 numeric page limit, all 75 page indices 0–74 fit; adding two index bytes gives 1,026 bytes per page.

These are **shape conditions against the analyzed candidate BOOT**. They do not identify the installed BOOT, establish full-image equality, signature or integrity acceptance, flashability, or successful restart. Instruction and limit semantics come from the [prior BOOT review](../../analysis/v4160-tx-image-integration-2026-10-22/image-plan/readme.en.md); this checker pins anchors without independently disassembling them. It reads only the APP windows specified above, no excluded APP range, executes no target and contacts no hardware.

Run: `python -B experiments/tsl9-bounded-boot-shape/check.py`.

The candidate BOOT's `E` handler `[0x231E,0x235C)` clears a nonzero active state, requests delayed callbacks `0x192C/200` and `0x20E2/400`, then requests an empty `E` response. The two instructions at `0x20E2` jump to `0x8000`. A connection to the APP entry above is conditional on this BOOT actually being installed, successful scheduling and callback execution, and the nominal APP mapping. Receiving `E` alone does not prove the delayed jump, restart, successful APP execution or whole-image integrity; the installed BOOT is unconfirmed.
# Bounded APP startup comparison

The official V4.1.60 APP and the existing TX-integrated candidate have identical initial 1 KiB pages `[0x8000,0x8400)` and reset windows `[0x186AA,0x18734)`. Their respective SHA-256 values are `90f03cc6687486011333937ddecd72767f464560f8039d66114ecf9e30250fe0` and `9507502c874a03e2c64a28b186a1f56aba9e85c9989dbf0cc053dabc4045bb4d`. At the nominal APP base, the entry JAL to `0x186AA` and reset's handoff JAL to `0x40000` match. The [checker](check.py) reads only these APP windows and BOOT anchors, not excluded ranges. Equality does not prove execution, installed resident identity, compatibility or safe flashing.

