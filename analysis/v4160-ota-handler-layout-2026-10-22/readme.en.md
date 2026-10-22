# OTA real providers, pointer escape and BOOT bounds

[繁體中文](README.md)

Actual `ld.lld -r` links combine the existing568-byte C11/C++17 component with real full-image provider objects. **All nine external references bind to allocated providers; only the original `__tsl9v4160_rom_entry` remains undefined.** This proves provider binding. **The original caller still invokes the old530-byte body, the new C function is not wired in, and no final ELF or new BIN exists.**

## Actual partial links

Both languages reuse receipt-verified existing `source-integrated.o` and `ota_handler.o`, without recompiling sealed sources. Real ET_REL outputs contain692 nonempty allocations (691 original plus the568-byte section) and8,281 relocations (8,261 original plus20). All original allocation bytes/relocation semantics remain, with both old raw handler and new FUNC568 present. No numeric ABS providers, stubs, fake FUNC extents or undefined-ignore options hide missing ROM.

`-r` does not prove final JAL application/reach, redirect the original caller, identify installed ROM or admit hardware. See [partial-link tooling/replays](provider-link/readme.en.md). [Shared C/C++](../../experiments/tsl9-v4160-ota-handler-compact/readme.en.md) remains568 bytes, with a38-byte original-placement excess.

## Real reply-pointer escape

S's two-byte response goes through `0x13E98` into packet assembly `0x13B4C`. Assembly saves source pointer/length in its live frame; the pointer also remains in A2 at allocator-like slot `+0x70`. Only afterward is the reread pointer sent as A1 to fresh copy slot `+0x4C`. Candidate copy leaves not comparing a specific stack range do not discharge numeric-address observability.

The new private reply occupies SP+6/7 while SP+12 savesS7; do not bind it blindly to the old location. A contents projection still needs slot70 to ignore/not retain ambient pointers, the candidate copy to be installed, valid RAM/no inappropriate alias or asynchronous observers, and downstream TX/release contracts. The review covers546 bytes /209 original instruction fields and five operand controls, without global ABI admission. [Consumers and conditions](reply-review/readme.en.md).

## BOOT numeric page bounds

Actual selected BOOT ID2580 command bytes (414 bytes /144 instructions) and a4-byte scheduled transfer establish unsigned pages0..95 with destination `0x08008000 + page*1024`, ending the final full page at `0x08020000`. Current Runtime contains76,800 bytes /75 pages, with numeric EOF `0x1AC00`. The subsequent21 pages /21,504 bytes are numeric guard headroom, **not free Flash, NV ownership, physical capacity, installed BOOT or updater acceptance**.

The bounded body does not establish a whole-image CRC/completion check; this does not prove absence of checks elsewhere in the update flow. See [raw fields/bounds and five controls](boot-review/readme.en.md). A worthwhile feature proposal is offline BOOT/Runtime partition preflight showing candidate page bounds and unknown device identity; it is not delivered hardware functionality.

## Unpromoted dispatch change

One full32-command C switch probe produces byte-identical568-byte /193-instruction C11/C++17 output. No new model or compiler-flag sweep. Actual object/IR/MD/receipts remain in the original workspace; published source/metadata does not advertise an unavailable archive as replayed. [Probe and explicit actual replay](dispatch-probe/readme.en.md).

## Limits and next work

Complete TX BIN SHA-256 remains `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`: thirteen original regions totaling930 bytes use readable C/C++ and an explicit ABI layer; remaining original carriers stay. The new partial object's568 bytes are not added to complete-BIN coverage or feature completion.

Next provider evidence concerns slot70 ambient A2/frame footprint. Placement still needs caller/continuation, Flash/NV/initializer ownership, relative branches and updater packaging. Valid out-of-line layout is worth investigating, without treating candidate page75 admissibility as free storage. Original hardware, ROM/BOOT, RAM/IRQ, Flash, BLE OTA acceptance/recovery remain unproved. [Plan](plan.en.md).

Only static reads, the C dispatch probe compile and partial linking occur. No RV32 execution/emulation, hardware operations, vendor API or UID/VIN transmission. D/P verification does not recompile the existing568-byte code or rerun unchanged HOST tests. Windows evidence does not establish Linux/macOS execution.
