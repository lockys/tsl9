# Actual partial link of record dispatch, predicate and prior dispatch

[繁體中文](README.md)

This experiment only runs existing LLVM `ld.lld -r --no-relax` on three formally checked genuine C/C++ objects:806B transport-dispatch,102B record-dispatch and42B eligibility predicate. No compilation, alias stub, wrapper, fake ABS provider, executable image or BIN is added.

The checker requires `.record_dispatch_component` to retain prior dispatch0..806, record806..908 and predicate908..950:950 bytes,330 instructions and42 genuine FUNCs (39 private architectural regions plus three small ordinary C functions). Cold/post-RET regions remain. There are50 pending RELA, six strong UND and zero global ABS.

Three genuine bindings are checked: original offset282 references `12a08` at806; record offset814 references existing status `81aa` at502 (the old reference at300 remains); record offset832 references predicate `821e` at908. The predicate's actual local branches are assembler-resolved; no fake relocation is introduced. All50 other machine control relocations remain pending. Symbol definition binding does not prove executable resolved transfers.

Remaining providers are `9454`, `9b36`, `12abe`, `14d2e`, `18ca4`, `16b7c`. Fresh resident copy `[0x4004C]`, transport admission `[0x4013C]`, tail `[0x40050]` and other opaque callees retain unknown identities/ABI. Initial length/status/config guards do not bound arbitrary then-live state after opaque calls. Successful transmission and peripheral identity are not inferred.

The checker freshly replays all three complete upstream formal proofs, including original bytes, typed operands, IR/SSA, MD, recipes, tools/resources and raw controls. New join checks use the sealed independent ELF32 parser for all body bytes, genuine symbol ownership, relocation remapping, complete allocation and330 LLVM raw rows. Seven source spans are freshly read from official V4.1.60 for non-control bits, RD/RS/RA link and original destinations. Prior source seals and complete transitive inputs are captured with current inputs. Actual in-memory ELF/operand controls exercise the gates without a whole-object hash shortcut.

From the project root, set `LLVM` to existing LLVM bin and use actual formal build roots:

```sh
python experiments/tsl9-record-dispatch-component/check.py
python experiments/tsl9-record-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --dispatch-root experiments/tsl9-transport-dispatch-component/build/component-v1 --record-root experiments/tsl9-record-dispatch/build/verified-v1 --predicate-root "$PREDICATE_ROOT" --build-root experiments/tsl9-record-dispatch-component/build/NEW
python experiments/tsl9-record-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-record-dispatch-component/build/NEW/c/verification.json
```

Default is source metadata only. `--folder MODE --receipt NEW` creates a new actual review; `--replay` is read-only. `--require-firmware-ready` must exit1. Receipts use `${TSL9_ROOT}`/`${LLVM_BIN}`; Python/POSIX wrapper has no personal hardcoded path. Previously denied Windows Git Bash is not retried; sh runtime remains unverified.

VMA0 is diagnostic and does not preserve original AUIPC placement meaning. Private regions are not independent ordinary C ABI functions. No whole-ROM, fault/IRQ/asynchronous, resident-provider ABI, physical-placement, hardware or flashing proof is claimed. No target/ISA/MMIO/HOST/network/hardware execution occurs. Firmware-ready, installed-ROM and physical-placement gates remain false.
