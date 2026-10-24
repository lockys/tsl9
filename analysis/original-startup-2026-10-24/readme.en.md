# Original startup and clock reconstruction

[繁體中文](README.md) · [Results](summary.json) · [C/C++ source](../../src/native/startup/boot_original.c)

The original header, default entries, reset, IRQ trampoline and complete clock path now share C11/C++17 source. The99 architectural regions are not99 ordinary C ABI functions.

| Scope | Verified offline evidence |
| --- | --- |
| 8000–8038 and18630–18834 | 572B/212 instructions, including61 original self-loops, twelve full-width NOPs and EBREAK |
| Clock1874A–18834 | Complete234B/93 instructions, including the18830 cold store and jump back to187CA |
| Initializer1AB60–1ABE0 | Entire128B emitted from the existing C array; section selection excludes diagnostic BSS/stack |
| Genuine partial link | Identical C/C++ products:572B code+128B data,82 RELA and3 UND; no ABS provider substitutes |

Every selected instruction matches after **data-only original-address relocation encoding**. This is not observed execution. Full source verification covers79 C/H files,53 units and106 comparisons/212 objects, preserving all prior104 results and625 artifact records.

Reset contains static GP20004000/SP20010000 constants, initializer source1AB60 and zero-end2000C958; these do not establish physical RAM capacity or ownership. The mstatus operation is CSRS with mask1888, not an unconditional final value1888. GP/SP/CSR/MMIO and private-register ports remain explicit, without an ordinary C calling-convention substitution.

Vector data8038, main entry9008 and resident ROM40000 remain unresolved. Vector/IRQ context, installed ROM, final memory placement, hardware startup and BLE OTA compatibility remain unproved. The VMA0 ET_REL product is **not a flashable BIN**. The older232B diagnostic clock source remains historical; different size alone does not prove incorrect behavior.

The [provenance index](publication-provenance.json) binds four portable original receipts without changing their bytes. The large complete curation receipt remains local and unchanged. The [vector frontier](vector-frontier.json) records only72 words from8038; neither complete vector length nor physical IRQ count is claimed.

Feature candidates are an offline image compatibility descriptor and read-only boot/clock diagnostics. Both require further complete-image/register evidence and neither was added to target execution. No target/HOST execution, ISA emulation, hardware, network or negative cases were used.

See [experiment and replay instructions](../../experiments/tsl9-original-startup/readme.en.md). These are uncommitted worktree changes; commit/push remain on hold because historical personal information was confirmed.
