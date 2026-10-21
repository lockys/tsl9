# Original callframe contract for a callable C reconstruction

The original initializer owns exactly `0x9A42..0x9AD2`: **144 bytes, 46 instructions**. Its four helper extents each contain 30 bytes/12 instructions. This review validates all 264 bytes/94 retained instructions against runtime SHA `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` and source seal `4d6745033aae496576b9db2fb7467396fbfda5067713cf1451a34b949b414283`. It reuses the sealed bounded decoder, independently decodes JAL and compressed frame operands, and records exact instruction boundaries. It does not execute instructions or compile a reconstruction.

At `0x9A42`, SP decreases by 16. The frame base is **entry SP minus 16**, not an assumed absolute RAM address. The save order is S2 at offset0 (`0x9A44`), RA at12 (`0x9A46`), S0 at8 (`0x9A48`), S1 at4 (`0x9A4A`). All four stores precede CSR800 clear88 at `0x9A50`. The original later sets CSR800 bits88 at `0x9AC2`, then freshly reloads RA@12, S0@8, S1@4, S2@0 at `0x9AC6/8/A/C`, adds16 to SP at `0x9ACE`, and RETs at `0x9AD0`.

Fresh reloads matter: the original returns those memory words, not abstract copies of the initial values. Equality with incoming S0/S1/S2/RA assumes the saved words remain unchanged. Frame alignment, asynchronous interruption and external stack modifications are not proved here. CSR set is not restoration of a previously saved CSR value.

| Call site | Four-byte JAL target | Link / continuation | A0 mask | A1 | Fresh word address |
|---|---|---|---|---|---|
| `0x9A5E` | `0x19142` | `0x9A62` | `0x02020006` | 1 | `0x4002101C` |
| `0x9A6A` | `0x19124` | `0x9A6E` | `0x101D` | 1 | `0x40021018` |
| `0x9A74` | `0x1917E` | `0x9A78` | `0x02020006` | 1 | `0x40021010` |
| `0x9A7E` | `0x1917E` | `0x9A82` | `0x02020006` | 0 | `0x40021010` |
| `0x9A88` | `0x19160` | `0x9A8C` | `0x101D` | 1 | `0x4002100C` |
| `0x9A92` | `0x19160` | `0x9A96` | `0x101D` | 0 | `0x4002100C` |

All calls encode rd=RA and signed JAL displacement in range, with even target alignment. They need not be four-byte aligned in RV32C. Each target is an actual helper entry, and each link is an exact initializer instruction boundary. Four-byte width and the original return link are concrete obligations; a J x0 tail transfer cannot substitute for a helper call.

The masks are cached using callee-saved roles: S2=88 from `0x9A4C` until both CSR operations; S1=`0x02020000` from `0x9A54`, used at `0x9A58/6E/78` with +6; S0=`0x1000` from `0x9A62`, used at `0x9A64/82/8E` with +29. Exact original helper bytes write only A0/A4/A5 and preserve A1 plus all three cached S registers, A2/A3, SP and RA. The helpers use no additional frame and return through the actual call link. The main's six reads must remain fresh even when an enable is followed immediately by disable; no cached word substitution is justified.

After the last helper, A0 is its last fresh READ32(`0x4002100C`) AND `0xFFFFEFE2`. The six trailing stores and CSR operation do not write A0 or A1. Normal output is A1=0, A4=128, A5=`0xE000E000`; main and helpers do not write A2/A3. S0/S1/S2/RA come from the fresh frame reloads. The retained caller proof establishes A3 passing through this call toward opaque callback `0x131E0`; its consumption is unknown, so preserve it. At the known initializer call `0x9258`, the incoming return link is `0x925C`; the function also needs to work with its actual incoming link rather than a hard-coded one.

## Concrete constraints for the next C implementation

Keep six **out-of-line**, byte-identical helpers at their original VAs. Preserve full helper A1 bits in the general helper API. Ordinary C ABI permits caller-clobbered A2/A3 and more scratch registers than this original contract; source types alone cannot preserve them. A compiler profile allowing original S0/S1/S2 caching needs actual save/reload and destination-register evidence, including the true prologue/epilogue and any outlined functions. It must not silently substitute different frame slots or claim pointwise equivalence from a normal return.

A normal RV32 C call pseudo can occupy **eight bytes** as AUIPC/JALR with a CALL relocation when relaxation is disabled. Six such pairs add24 bytes relative to these original four-byte calls. No call width for new code is proved here. Any deliberately scoped direct-JAL primitive or linker relaxation must be independently reviewed for argument/clobber semantics, linkRA, all six displacements and boundaries; do not enable broad relaxation or weaken exact section assertions merely to make a size check pass. The source design is not an authorization to change compiler settings.

Verify the candidate's actual C/C++ object and linked machine code, exact helper identity, six call order/targets/link encodings, 16-byte frame if claimed, CSR clear/set order, all fresh RMWs, tail widths, final A0/A1/A4/A5 and preservation of all required registers. A compiler's different valid normal frame layout is not the original stack effect. Measure size again; neither fitting144 nor placement nor asynchronous IRQ equivalence follows from using calls.

Eleven specific raw mutations (frame size/save/load slot, call rd/target, mask constant, CSR source, return register, final flag and tail width) are actually made in memory and rejected by the retained-source gate. They are static source controls, not compiled mutants. The ledger preserves raw rows, geometry, exact input hashes and all limitations. No model/old proof edit, compilation, ISA execution, network, hardware access or BIN generation occurs.
