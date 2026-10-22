# Original App BLE configuration fields and candidate header ABI

[繁體中文](README.md)

This bounded scope reads ID2966 `0x199E2..0x19B16` (308 bytes) and two retained official SDK headers. It does not execute target code or establish call/MMIO effects, installed ROM or Flash ownership.

## Actual compiled structure layout

Pinned Windows NDK Clang targeting `riscv32-unknown-elf / ilp32` includes each actual V1.40/historical header. `config_layout.c` emits the same `offsetof`/`sizeof` values in each object. Each object has one40-byte read-only data allocation, no relocations, no true undefined symbols and no executable contents. No RV32 execution occurs.

| Field | Offset |
|---|---|
| MEMAddr/MEMLen | 0/4 |
| SNVAddr/SNVBlock/SNVNum | 8/12/14 |
| staCB | 52 |
| readFlashCB/writeFlashCB | 56/60 |
| sizeof(config)/sizeof(status callback pointer) | 64/4 |

This is a candidate SDK type ABI. A header declaration does not establish that installed callbacks ignore ambient A2.

## Visible original App fields

Actual bytes corroborate32 selected instruction fields and23 standard store instructions in the308-byte body, without claiming semantic interpretation of all106 instructions.

- The original frame is96 bytes. `19A20/19A2E/19A34..19A38` request nominal slot40048 with A0=currentSP+16, A1=0 and A2=64. The function name does not prove zeroing succeeds; S0/SP preservation across preceding calls remains conditional.
- AUIPC/ADDI/SW at `19A3A/19A3E/19A42` establish numerical MEMAddr `0x2000418C`; the MEMLen halfword is `0x7000`.
- `19A4A/19A4E/19A52` establish `0x08078000-1024 = 0x08077C00`, stored at SP+24, candidate config+8/SNVAddr. **This is neither a complete NV-write extent nor proof that appended0x1AC00 is free.** Unknown calls, aliases, block defaults and Flash callbacks remain boundaries.
- Explicit stores at SP+72/76 correspond to candidate readFlashCB/writeFlashCB. No explicit SP-relative store overlaps SP+68..71/staCB. Intervening calls and indirect stores prevent inferring a zero value at BLE_LibInit or permanent zero thereafter.
- `19AE2..19AEC` freshly load nominal400A4 and call with A0=currentSP+16. [Actual candidate bulk-copy writers](../callback-review/readme.en.md) copy config+52 into the allocator callback word. This identifies a conditional field origin, without inventing a live value.

Five raw negative controls change only an admitted instruction immediate, retaining the opcode and other fields before requiring semantic rejection. The first unpublished filter counted decode failures as controls; it was corrected and its history retained under build. Published historical seals and original artifacts were unchanged.

## Reproduction

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware FW --layout-receipt BUILD/verification.json
python3 -B probe.py --project-root ROOT --headers V140_HEADER V131_HEADER --tool-dir LLVM
python3 -B probe.py --project-root ROOT --replay BUILD/verification.json
```

Default check reads source/field metadata only. Explicit firmware reads actual App bytes; an explicit layout receipt rereads actual header/object inputs. Probe compilation requires the two exact actual headers identified by complete hashes in selected metadata. Python interfaces are portable; native tool proof is Windows NDK only, without Linux/macOS/CI claims. Readback and compile logs are separate. No HOST/RV32 execution, ISA emulation, network, device IDs, BLE/UART/CAN/Flash or new BIN occurs.
