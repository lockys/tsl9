# Page reply: explicit source ABI ordering

[繁體中文](README.md)

This narrow backend restores two instruction-order regions in a freshly
compiled standalone `tsl9_ota_page_reply_9b8e` function. Its input must be a
124-byte / 50-instruction RV32 RVC soft-float ET_REL object with one allocated
function and one actual `R_RISCV_JAL` reference to
`__tsl9v4160_call_8a56`. It is **not an opcode generator or a firmware loader**.

The first region, function offsets `[0x02,0x16)`, contains six compiler stack
saves, `LUI S2`, and the allocator-slot `LW A5`. The second, `[0x58,0x60)`,
contains the release-slot `LW T1` and restores of RA and S0. The policy names
the decoded register/operand operations. Every output word comes from the
same region of the actual new compiler input. No original BIN, embedded
instruction template, padding, or fallback is used for generation.

The order is an explicit source ABI contract. LLVM alone did not produce it.
Moving a resident pointer load among stack stores can change fault or
asynchronous prefixes, particularly if storage aliases. This backend does
**not** claim arbitrary pre/post compiler semantic equivalence. It admits the
specific source instruction stream and records that additional stage.

## Run

Use Python 3.10 or newer. Paths are explicit and must resolve inside the
selected project root. Outputs and receipts are create-only. The pinned ELF
parser and independent raw decoder must also be available in that project.

```sh
python experiments/tsl9-v4160-reply-abi-order/order.py \
  --project-root . --input path/to/fresh/page_reply.o \
  --output path/to/new/reply-ordered.o \
  --receipt path/to/new/order-receipt.json

python experiments/tsl9-v4160-reply-abi-order/order.py \
  --project-root . --replay --receipt path/to/new/order-receipt.json
```

The standalone native compiler object uses a real GLOBAL FUNC / size 124.
The original complete image instead has a public NOTYPE / size 0 entry and
a separate local incoming entry. This standalone pass does not invent or
change those complete-image roles; it rejects complete-image input objects.

## What is checked

The pass checks instruction boundaries, the two exact compiler-order
inventories, required source operands, fixed call/branch/return positions,
section ownership and attributes, symbol/relocation anchors, and file-storage
aliases. It rejects reapplication and unexpected input. All bytes outside the
two regions remain unchanged, including metadata, symbols, relocations, and
the unresolved TX JAL placeholder. The post-transform stream is independently
decoded and compared with all 50 source operations, with that one actual JAL
relocation normalized to its declared source destination.

Read-only replay recomputes the complete transform and receipt, then compares
the actual input/output bytes and retained metadata. The tool records its own,
policy, ELF-parser and raw-decoder hashes. It does not authenticate the input
C/C++ compiler provenance by itself: the component compiler verifier must do
that separately.

No CPU state or target instructions are executed or emulated. Unknown resident
SP/S-register preservation, pointer-table validity, physical hardware, full
image integration and BLE OTA compatibility remain separate requirements.
No flash-readiness claim is made.
