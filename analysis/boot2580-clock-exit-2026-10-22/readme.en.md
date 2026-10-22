# Original clock normal-exit contract

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

This source-contract draft is not a new native implementation. The checker rereads official BOOT ID2580 and Runtime ID2966, verifies the same234B/93 instructions and published source ledger, classifies every own-written RD, checks exit operands and both reset suffixes. It does not execute HOST/ISA/target/MMIO, compile or access the network.

## Contract and premises

**W** denotes the complete u32 freshly loaded by BOOT `0x2CF8` / Runtime `0x187CA`, `LW A4,12(SP)`.

| Normal RET condition | A2 | A3 | A4 | A5 |
|---|---|---|---|---|
| Fresh `W != 1` | `0x20000` | `0x40021000` | full u32 `W` | `1` |
| Coherent private stack, no interference; skip | same | same | `0` | `1` |
| `W == 1`, both later polls return normally | same | same | `8` | `8` |

All rows require the checked original code, no asynchronous code/GPR/control-flow interference and normal completion of the relevant accesses/RET. They are conditional normal-exit results; the two later polls need not terminate. The second row additionally requires a valid disjoint coherent private stack without external/alias writes, so the selector0/1 store is read back unchanged. The broader arbitrary-live-word scope varies that memory observation only, not arbitrary GPR/control-flow state. It cannot inherit the stronger A4=0 claim. A0 is not a success result.

## Last writes in original code

| Role | BOOT PC | Runtime PC | Raw / operand |
|---|---|---|---|
| A2 fixed | `2C8C` | `1875E` | `37060200` LUI A2,0x20 |
| skip A3 | `2CCA` | `1879C` | `b7160240` LUI A3,0x40021 |
| fresh W / skip A4 | `2CF8` | `187CA` | `3247` LW A4,12(SP) |
| skip A5 | `2CFA` | `187CC` | `8547` LI A5,1 |
| skip edge | `2CFC` | `187CE` | `631ff704` BNE A4,A5,2D5A |
| configure A3 | `2D40` | `18812` | `b7160240` LUI A3,0x40021 |
| configure A4 | `2D50` | `18822` | `2147` LI A4,8 |
| configure fresh A5 | `2D52/54` | `18824/26` | `dc42/b18b` LW A5,4(A3); ANDI A5,12 |
| configure exit | `2D56` | `18828` | `e39ee7fe` BNE A5,A4,2D52 |

The skip branch reaches shared SP restoration/RET without changing A4=W or A5=1. Normal exit from the configure poll requires masked A5=A4=8. Complete RD inventories establish no later A2 write and the listed final A3 writes on both paths; no generic ABI assumption substitutes for source evidence.

## Static conditional counterexamples

- Allowing fresh W=`0xDEADBEEF` yields skip A4 equal to that value, A5=1. General live-word semantics cannot claim A4 always0.
- A ready sample in the first poll followed by fresh control bit17=0 at `0x2CEA` still selects skip with coherent private stack. Earlier readiness is not the fresh observation.
- Counter4096 can end the first poll, yet fresh bit17=1 at `0x2CEA` selects configure. Earlier timeout samples do not decide the last state; the remaining polls still govern normal termination.

These are source-derived conditional data choices, not execution, emulation or hardware observations.

## Reset suffix and live values

BOOT call `2C4E` returns to `2C52`; Runtime call `18720` returns to `18724`. Each has4 subsequent instructions: AUIPC T0, ADDI T0, CSRW MEPC,T0, no-link JAL x0,`40000`. BOOT sets MEPC=`1A52`, Runtime=`9008`. The checker directly verifies all10 call/suffix raw instructions and operands from the original files, without old absolute-path receipts.

Neither suffix reads/writes A2–A5 or calls another callee. The residues are forwarded unchanged to the external resident boundary: **they are not proved dead**. Whether resident/downstream code, IRQs or hardware observe them, and installed resident identity, remain unproved.

## Replay

```sh
python analysis/boot2580-clock-exit-2026-10-22/check.py --project-root .
```

`--emit-ledger` prints draft JSON only; it never writes files. Default replay rereads both original images/tracked dependencies, compares [ledger.json](ledger.json), and rejects6 actual raw-operand XOR mutations: A2 constant, fresh slot offset, A5 literal, skip polarity, A3 destination and final mask. Mutants run operand gates, not merely a whole-firmware-hash rejection. The full93-row table remains in the [published clock evidence](../boot2580-clock-2026-10-22/README.md).
