# NV write offline component: independent ELF review

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

This review independently rereads actual C/C++ `native.o` files and actual `linked.elf` outputs. Producer verdict fields and producer replay are not used as the decision. The checker does not compile, link, execute target/HOST/CPU/ISA/ESIL code, access MMIO/hardware, use the network, or generate a BIN.

Both input ET_REL objects have SHA-256 `b30c679bd1e15a7a59be59b4ed723a6f98f78cc022e93e314e4c59f85c7aa09f`. Both linked `.text` sections have SHA-256 `bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`.

|Real definition|Bytes|Component VA, hex|
|---|---:|---:|
|tsl9_flash_status_18e90|8|0|
|tsl9_flash_unlock_18e98|30|8|
|tsl9_flash_lock_18eb6|14|26|
|tsl9_flash_erase_18ec4|46|34|
|tsl9_flash_program_18ef2|100|62|
|tsl9_flash_quarter_9c0a|64|C6|
|tsl9_delay_19764|60|106|
|tsl9_nv_write_callback_197be|72|142|
|Total|394|End 18A|

All eight nonzero global FUNC definitions come from real input sections and remain complete: 394 bytes and 148 instructions. VMA zero is an offline link location, not a physical address. Entry is the actual write symbol at VA 0x142. Six functions are reachable through these calls from write; the unused status and quarter functions are also retained completely, without GC.

## Calls and complete byte preservation

There are ten real input relocations: five `R_RISCV_JAL` (type17) in quarter and five `R_RISCV_CALL_PLT` (type19) in write. The output has no UND, remaining REL/RELA sections, or ABS address providers. The checker reconstructs targets from actual JAL immediates and AUIPC RA/JALR RA,RA pairs, then checks each target against its genuine output FUNC definition. Disassembler symbol annotations are not accepted as the proof.

Every input/output function byte is compared. Only five JAL immediate fields at bits31..12, and five CALL_PLT AUIPC bits31..12/JALR bits31..20, may change: 260 editable immediate bits. Opcodes, rd, rs1 and all other fields must remain identical. The 60-byte spans containing relocation instructions are not broadly exempted.

Only 24 bytes actually change: 15 in quarter and nine in write. All six other functions are byte-identical. Both actual LLVM static logs independently match every original/linked instruction byte and PC: 788 function bytes and 296 instruction rows are reread. These instructions are never executed by this checker.

## Segments, providers and metadata

The actual link recipe is `ld.lld --no-relax -T component.ld native.o -o linked.elf`, without GC, numerical providers, ROM stubs or additional objects. The actual script places `.text.*` at VMA zero, uses the real write symbol as entry, and discards only `.comment`.

The only allocated section is the complete 394-byte RX `.text`. The sole PT_LOAD has file/memory sizes394 and covers exactly that section, without ELF headers, holes, extra payload or NOBITS. A separate PT_RISCV_ATTRIBUTES exactly matches a nonallocated, flags-zero, 64-byte `.riscv.attributes` section. This read-only metadata is not a loadable code allocation.

`ABS_providers=0` does not mean zero SHN_ABS metadata symbols: one local STT_FILE filename and one local zero-size/zero-value `$d.N` mapping symbol remain. Only these exact metadata forms are exempted. Replacing a genuine function provider with ABS is still rejected.

## Actual checks and replay

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --component-receipt /absolute/build/component-v2/c/verification.json --receipt /absolute/new-review-c.json
python3 -B check.py --project-root ROOT --replay /absolute/new-review-c.json
./check.sh --project-root ROOT --replay /absolute/new-review-c.json
```

On Windows use the installed Python directly. Default mode checks sealed metadata/source pins without reading actual object/linked ELF and reports `actual_artifacts_read=false`. Explicit receipt mode rereads artifacts and creates a previously nonexistent review receipt. Replay rereads the same actual evidence and remains read-only. Source-pin lookup supports workspace/publication layouts; absolute paths retained in actual logs/receipts must still exist.

Seven controls mutate the actual linked ELF in memory: wrong CALL_PLT target, section size, LOAD memory hole, writable LOAD, fake ABS provider, wrong FUNC size, and a changed byte in a retained unused function. All are rejected by the independent gate. Mutated content is never executed or exported as ELF/BIN. Actual C/C++ review and read-only replays pass. New text uses LF with a single final newline; README.md is identical to readme.zh-TW.md. The previously denied Git Bash was not retried; the Python entry point was verified.

The first component-v1 producer reader incorrectly required one program header when only one LOAD was intended, rejecting normal attribute metadata. Its failed output remains in build/component-v1. Component-v2 changes only that reader, with no C/C++ instruction/source, linker flag or script change. This review checks both actual program headers separately.

## Limits retained

This proves genuine definitions, actual relocation resolution and complete static component preservation. The original `source-review` seal is `c29430e22451a71a2acbcf0afea199f4b6053d09309597eb4082a52fbafa677a` and is unchanged.

Full original ABI and normal caller replacement remain unproved: new write has a 16-byte frame; the original has a 32-byte frame and freshly reloads the saved source. New timer also has different scratch/output GPRs. Successful component linking cannot resolve these differences or establish fault, IRQ, asynchronous or alias equivalence, installed providers, Flash ownership, poll termination, OTA or physical write success. No flashable BIN was generated.
