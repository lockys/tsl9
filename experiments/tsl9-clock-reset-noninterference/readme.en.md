# Whole clock and conditional preservation of reset state

[繁體中文](README.md) · [Prior reset/bootstrap proof](../tsl9-reset-state-bootstrap-contract/readme.en.md) · [Current formal reconstruction](../tsl9-event-word-table-integration/readme.en.md)

This audit covers all **234B / 93 instructions** of `0x1874A..0x18834` in `boot_original.c`,including the `0x18830` cold store and `0x18832` backedge. Every original byte equals current native C11/C++17 original-coordinate ELFs. The whole CFG is reachable and its16-byte frame is restored at the normal return. The older232B `clock_init.c` diagnostic remains historical;this proof uses the complete original path.

## CPU accesses and return contract

Finite CFG constant propagation retains every branch and treats every loaded memory value as unknown. It reads no live MMIO/RAM and performs no target execution or memory simulation. All22 word loads and21 word stores have effective addresses among these five numerical locations:

| Role | Addresses |
| --- | --- |
| Nominal MMIO | `0x40021000`,`0x40021004`,`0x40021008` |
| Original own frame | `0x2000FFF8`,`0x2000FFFC` |

These roles require the original valid,nonaliasing memory map;they do not prove physical peripherals or SRAM mapping.

- Every explicit CPU store avoids the prior four groups of ten counter/sequence/mode bytes.
- The original `SW zero,12(SP)` at `0x18830` writes `0x2000FFFC`. Both the cold store and its backedge are included.
- There are no other callees,CSR writes,or GP/RA writes. With caller GP=`0x20004000`,SP=`0x20010000`,RA=`0x18724`,the sole normal return at `0x1882E` preserves those values.
- The first MMIO load at `0x1874E` remains before frame allocation at `0x18754`;that ordering is not moved.

## Implications for startup state

The prior proof establishes zeroed state at `0x186F8` after normal reset clearing,and shows that known bootstrap writes avoid those state bytes. This audit supplies the intervening clock's explicit CPU-write and normal-return contract. Conditional zero preservation can therefore extend through the clock and known bootstrap/MRET path when:

1. Original placement,entry registers and instruction semantics hold,and all accesses complete normally.
2. MMIO/SRAM are nonaliasing,with no IRQ/DMA,MMIO-triggered indirect writes,faults or reentrant interference.
3. Clock polling reaches its normal return,and installed resident code/source memory match the candidate,including the still-unprovided four-byte SDK second-copy source.

**This does not prove physical startup completion,live MRET values,or first-use lookup values.** Peripheral side effects,polling liveness,frequency,IRQ state,installed ROM,later writers and callback ordering remain open. Original polling and cold paths are retained without forcing success or declaring a global mode/counter domain.

## Replay

With the fixed local native artifacts and LLVM available,run from the repository root:

```sh
python3 experiments/tsl9-clock-reset-noninterference/check-v1.py --tool-dir "$LLVM_BIN"
```

[Inputs](inputs-v1.json) · [Full address/register receipt](verification-v1.json) · [Unimplemented diagnostic idea](feature-candidates.json)

Formal APP sources and native artifacts are unchanged:**164 C/H files,95.75% static byte coverage,and six unresolved source providers**. No new firmware CODE/DATA,BIN,target/HOST-model/ISA execution,hardware access,or third-party API requests occurred.
