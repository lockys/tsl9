# OTA packet construction: readable C/C++ and unresolved native boundaries

[繁體中文](README.md)

This round follows the reconstructed page reply's direct callee in official ID2966 V4.1.60, `0x8A56..0x8B6E`. All original 280 bytes / 96 instructions are decoded, with forty rejected operand mutations. The recorded object's nine external entries target the function start; one does not establish a return link. RELA type alone does not distinguish every ordinary call from a no-link transfer.

## Confirmed original logic

The entry checks full unsigned A3 and returns before creating a frame when it exceeds 1039. Connection values come from live GP `+0x96` and `+0x9A`. Each gate reloads a service pointer from `0x4013C`; only an exact full-width return value of 1 selects a lane. A2/A3 at the second call may be residues of the first call. Candidate SDK prototypes cannot remove or zero them.

The selected descriptor starts at `0x2000B18C + lane * 1062`. The packet begins at `+6`, containing 16-bit `0x7F55`, command, length fields, byte-by-byte copied payload, and the low-eight-bit additive checksum of command/length/payload. Descriptor length and zero fields are each 16-bit stores. A byte read from live GP `+0x94 + 4 * lane` supplies the final A0; A1 is 1 and the function tails through a freshly loaded `0x40050` pointer.

There are no visible allocation/free or memcpy calls in this body. Direct buffer construction and service handoff do not demonstrate actual Bluetooth transmission, reception or update success. The initial length guard does not prove that an unknown ROM call preserves the subsequent live S0 bound.

## Evidence levels

| Item | Current evidence |
| --- | --- |
| Original instruction fields and source roles | Checked; see `source-review` and the corrected public `source-review-v2` entry |
| Readable C/C++ logic | Added in `experiments/tsl9-v4160-ota-tx`; synthetic host and native compilation evidence are separate |
| Synthetic host behavior | Each language: 107 cases / 15,605 checks and eight rejected compiled semantic negatives |
| Independent source effects | Each language: 31 cases / 78,283 checks and fourteen rejected compiled semantic negatives |
| Native section size | Both compile probes have 280 bytes / 96 instructions |
| Original machine code, entry and restore ABI | **Not admitted:** frame precedes the original guard, restores are late, some operands/control flow differ |
| Complete image | Previous twelve-function / 650-byte image remains; TX still uses its original carrier |
| Board, ROM/BOOT, BLE OTA and recovery | Unverified; no flashability claim |

Independent ABI review finds that an existing-word permutation alone cannot close these differences. No original opcode filling, old-scheduler expansion or weakened replacement gate was used. Passing source-effect tests cannot override the native rejection.

Future integration must separately prove the roles of all eight original private boundaries, the PCREL pair and call continuations. The original RAM-pair anchor is `+0x80`; the compiler uses `+0x74`. The second gate continuation moves from original `0x8AB6` to `0x8ABA`. Equal total size does not justify retaining old offsets or treating every private symbol as a disposable branch label.

## Checks and follow-up

```sh
python experiments/tsl9-v4160-ota-tx/verify_host.py --project-root . --language both
python analysis/v4160-ota-tx-2026-10-22/source-review-v2/check-review.py \
  --project-root . --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
python analysis/v4160-ota-tx-2026-10-22/continuation-plan/check.py \
  --firmware /absolute/path/ID-2966-V4.1.60-decoded.bin
```

The workspace uses prefix `apk-analysis/tsl9-`; delivery and publication use `analysis/`. Default source checking rereads the original BIN and source records. Actual object replay requires an explicit object argument. `source-review-v2` only corrects the previous public checker's JSON tuple/list comparison; original decoder, contracts and sealed bytes remain unchanged.

The [static input check](inspection/readme.en.md) records actual REA provider availability and the independent LLVM scope. The [continuation plan](continuation-plan/readme.en.md) tracks shared-buffer references in `0x8614`, SDK candidates and offline packet preflight / update wait-reason proposals. The full objective still requires necessary application and execution-layer reconstruction plus hardware and OTA compatibility proof, and remains incomplete.
