# Original event callback8614: source contract

[繁體中文](readme.zh-TW.md)

Official ID2966 V4.1.60 callback `0x8614..0x888C` is632 bytes, SHA-256 `3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf`. Firmware file base is0x8000, so the actual file slice is0x614..0x88C.

`instructions.json` retains217 full operand records. A small single-instruction bit-field decoder agrees with independently normalized LLVM operands. There are26 direct control edges,64 memory instructions and15 indirect JALR calls. Twenty-six controls deliberately change a decodable, same-width semantic field before checking rejection; a changed file hash is not their rejection criterion. No CPU state machine, ISA interpreter, emulation, network or device operation is used.

`contracts.json` contains reviewed flow, widths, frame and15 call projections. A0 is a full32-bit context and A1 a full32-bit event word. Priority is low16 sign bit(mask0x8000), then mask0x8(bit3) before lane lookup, then fresh byte matches atGP+94/+98 against the full context, then lane masks1/2/4. Mismatch or no supported lane mask returns0. Completed paths compute **live S0 XOR the handled mask**, not a uniform success code or a blanket flags clear.

The message path obtains a pointer, unconditionally reads its type intoA4, optionally dispatches typeB0 with pointer+8 and the byte atpointer+4, then invokes a release candidate using liveS1. Purpose names are inferences, not identified SDK functions.

Mask1 uses1062-byte buffer stride and8-byte descriptor stride. Its first gate requires **exactly1**. The16-bit wrapped total-minus-cursor is sign extended; nonpositive values clear the pending16-bit length. Another slot returns a value truncated to16 bits after subtracting3. Later signed comparison, descriptorSH, bufferSB10 and slot-call order are source facts. Reducing this to a conventional minimum operation requires additional callee-preservation assumptions.

Mask2 clears pending length when the count byte is zero. Otherwise it obtains a pointer and SWs it todescriptor+4 **before testing null**. Copy source uses a freshly read cursor plus liveS3/S9; length is freshly read. Only after copying does it obtain freshGP/gate state. This gate tests **A0&1**, unlike the exact1 gate. Success writes a freshGP+2A value into the descriptor, calls another slot, and advances a16-bit cursor only on zero return. Failure/null paths decrement an8-bit count and call a scheduling candidate.

Mask4 explicitly supplies `(S5,12,24,0,200,S4)` with targetA6. Mask8 supplies `(entry A0,0,0x19DE0)`. Unspecified arguments are not synthesized zero, and intervening scratch writes matter. `assigned_args` and the C argument mask are explicit projections, not complete rawA0..A7 or asynchronous-prefix equivalence claims.

The original48-byte frame savesS0,RA,S1..S9 in recorded order. Its common epilogue freshly reloadsRA,S0..S9 from **current liveSP**, adds48 to thatSP, then jumps through freshRA. Unknown opaque calls may changeGP/S/SP/frame memory or never return. EntrySP restoration, original callerRA and ordinary callee preservation are therefore conditional rather than established physical facts.

The original carrier has36 owned relocations:26 control references plus fiveHI/LO pairs, alladdend0. Twenty-four private roles comprise19 control targets and fivePCREL anchors. Three external addressHI20 references from init_8e88 offsets64/250/272 target the genuine NOTYPE0 callback entry. No directJAL incoming is recorded; indirect/computed references remain unknown. Separate entry-plan evidence owns registration/buffer-init details; registering an address does not prove device execution.

Default checks read the official BIN and retained source/reference fields. Optional `--original-object` reads actual original carrier sections/symbols/RELA and reports that separately. It expects the original callback body and does not validate a new native replacement.

```sh
python3 -B check-source.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python3 -B check-source.py --project-root /project --firmware /absolute/ID-2966-V4.1.60-decoded.bin --original-object /absolute/source-integrated.o
```

`source-reconciliation.json` binds four frozen C/H files and records read-only algorithm reconciliation. HOST return_address is saved-frame bookkeeping rather than the architectural link for every opaque call; ordinary C return does not physically JR that numeric value. Source proof and C/HOST/native reconciliation are separate. Passing original operands proves neither native fit/fullABI nor flashing/OTA compatibility. UnknownROM, hardware and asynchronous behavior remain unverified.
