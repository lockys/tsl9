# CH32V208/D8W candidate link contract review

Scope: local, read-only inspection of the existing R81 source/ELF/evidence; this review did not link, compile, execute or emulate target code, access hardware/network, or change re-tsl9, old checks or seals. Only this new review directory was written. The current candidate SCOPE.md explicitly admits the two address assumptions below. This is a new experimental profile and does not revise the old strict result.

## Decision

Fixed-original-VA final linking followed by objcopy to an APP-base-0x8000 binary is reasonable **as an experimental artifact contract**. Bind only `__tsl9_rom_entry = 0x40000` and `__tsl9_opaque_address_19d10 = 0x19D10` as zero-size ABS/NOTYPE external address assumptions. Require a strict successful final link with no other named UND symbols. No executable ROM section, table allocation, dummy function or ignored undefined symbols may be added. Address resolution establishes neither provider identity nor executable/ABI/data extent validity.

The existing R81 ET_REL memory object has exactly those two named UND symbols, SHA256 `e60e2df377b398c564e18203de2669da62cb8745309eeb29061aa1c17ff04eab`, 335728 bytes. Its recorded strict final-link fails on both symbols. Preserve that result and `audit-native.py`'s strict-two-UND assertion unchanged.

## Critical linker input detail

The actual memory object contains already-coalesced input names `.tsl9_code_00008000`, `.tsl9_ro_00008038`, etc. Their ET_REL `sh_addr` values are all zero: the hex suffix is the placement map, not an already-established executable VMA. Reusing the old script's input selectors such as `*(.text.tsl9_image_entry)` against this object would not select the coalesced inputs. Generate explicit final sections using the actual input names and recorded numeric VA/size. Never let orphan placement decide them.

The following is a **design excerpt**, not a complete linker script. Expand it to every verified existing code/RO section and every source-backed carrier interval, retaining exact size assertions and non-overlap checks:

```ld
OUTPUT_ARCH(riscv)
ENTRY(tsl9_image_entry)
__tsl9_rom_entry = 0x40000;
__tsl9_opaque_address_19d10 = 0x19D10;
SECTIONS {
  .tsl9_code_00008000 0x8000 : AT(0x8000) {
    KEEP(*(.tsl9_code_00008000))
  }
  .tsl9_ro_00008038 0x8038 : AT(0x8038) {
    KEEP(*(.tsl9_ro_00008038))
  }
  /* Every other original-VA code/RO input explicitly placed here. */
  .tsl9_ro_0001a2d0 0x1A2D0 : AT(0x1A2D0) {
    KEEP(*(.tsl9_ro_0001a2d0))
  }
  .tsl9_runtime_ram 0x20004000 (NOLOAD) : {
    KEEP(*(.tsl9_runtime_ram))
  }
}
ASSERT(tsl9_image_entry == 0x8000, "APP entry drift")
ASSERT(tsl9_reset_entry == 0x183FE, "reset drift")
ASSERT(__tsl9_data_load == 0x1A7E0, "initializer drift")
ASSERT(__tsl9_data_start == 0x20004000, "RAM start drift")
ASSERT(__tsl9_bss_end == 0x2000C950, "RAM end drift")
ASSERT(__tsl9_stack_top == 0x20010000, "observed SP drift")
ASSERT(SIZEOF(.tsl9_runtime_ram) == 35152, "RAM span drift")
```

Use strict linker defaults / `--no-undefined`, `--no-relax`, no `-r`, no undefined-ignore option, and fail on unexpected allocated orphan sections. Review any nonallocated attributes/debug/metadata policy separately; do not silently discard an unexpected allocated section. Explicit `AT(VA)` on file-backed Flash intervals avoids inherited LMA drift. If PHDRS is introduced, verify it independently: RAM must not become an enormous file-backed load span.

## Entry, reset and initialization constraints

| Item | Required original numeric contract |
|---|---|
| ELF entry | `tsl9_image_entry = 0x8000`; 4B `JAL x0` to `tsl9_reset_entry = 0x183FE` |
| Reset combined section | 148B at 0x183FE; active reset prefix 138B, private MRET at 0x18488, existing defaults 0x1848C/0x18490 |
| GP | 0x20004000 from original 0x183FE/0x18402 AUIPC/ADDI pair |
| SP | 0x20010000 from 0x18406/0x1840A; existing zero-size ABS address only |
| Copy | 136B = 34 words, source `[0x1A7E0,0x1A868)`, destination `[0x20004000,0x20004088)` |
| Zero | 35016B = 8754 words, `[0x20004088,0x2000C950)` |
| RAM container | `[0x20004000,0x2000C950)`, 35152B, NOBITS/NOLOAD |
| mtvec | original construction 0x8038, OR 3, CSR value 0x803B |
| Clock call | 0x18474 JAL ra to 0x1849E, ra becomes 0x18478 |
| mepc | 0x8FE6 at original write 0x18480 |
| ROM tail | 0x18484 JAL x0 to 0x40000, **no return link to 0x18488** |

The initializer is already physically allocated once inside the 2204B union `[0x1A2D0,0x1AB6C)`: `__tsl9_data_load` is a 136B OBJECT at section offset 0x510. Its VMA and LMA are 0x1A7E0, because the existing reset explicitly copies from that Flash address. Do not create another `.data` load image or relocate it to RAM VMA. The first 136B of the RAM NOBITS reservation become initialized only through reset; its `.zero` assembler directives do not mean those bytes belong in the binary. Objcopy must exclude the RAM reservation and must not manufacture a ~512MB span.

Preserve original instruction widths/opcodes/registers, all HI/LO anchors, the five CSR writes (0xBC0=31, 0x804=3, mstatus OR 0x1888, mtvec, mepc), original clock call and unconditional ROM tail. The final numerical instructions should be checked, not inferred from symbol-table addresses alone. Normal clock return and ROM eventual transfer/MRET are still runtime premises.

## File coverage and remaining unknowns

Runtime source is 76800B at modeled `[0x8000,0x1AC00)`. Objcopy emits from the lowest selected file-backed LMA, not from ELF ENTRY. Require lowest LMA 0x8000 and verify each BIN offset equals LMA minus 0x8000. To retain a complete 76800B runtime-shaped image, fill gaps only with explicitly source-backed original-byte C/C++ carrier sections, each with provenance and hashes; zeros/FF inserted by objcopy gaps or gap-fill are not source evidence. A shorter/sparse result must not be described as the full original span. No output bytes at ROM 0x40000 or unknown `[0x1AC00,0x1AD10)` may be synthesized.

The 0x19D10 raw-U8-derived lookup domain spans 4096B to 0x1AD10. The retained runtime provides at most 3824B of that address range, leaving the final 272B absent. A symbolic base-address binding does not allocate or prove the complete table and does not prove every input remains within retained bytes. Existing RO overlaps are not permission to assert object type or full provider extent.

The 1572B BLE compare view is a conditional source view inside the 2204B union. Its byte-count interpretation, no-overread behavior, normal ROM return, callee-saved registers and valid pointers/stack remain premises. Neither the two ABS symbols nor successful link/objcopy proves resident ROM identity/code, BLE ABI, low-RAM callbacks, physical SRAM/stack/IRQ ownership, MCU/PCB/crystal identity, boot/root supply or OTA acceptance. SP's 14000B numerical gap above 0x2000C950 is not proven usable stack. BOOT/ROOT/ROM are outside this runtime artifact.

## Required independent artifact checks

1. Record C and C++ source/tool/command/input hashes. Assert candidate assumptions exactly match the two names/values above, both ABS/NOTYPE/size0; existing SP remains address-only. No new table, ROM allocation or dummy body.
2. Confirm ET_EXEC, RV32/RISC-V ABI/flags, ELF entry0x8000, zero named UND and no unresolved runtime relocations. Retain old strict-two-UND receipts and source hash guards.
3. Compare every final alloc section's name/type/flags/VMA/LMA/size against the explicit placement plan. Reject overlap, drift, unexpected allocated orphans, and unexpected PROGBITS RAM; count the single initializer allocation.
4. Decode final reset/entry and important relocated callback/jump-table references numerically; compare original opcodes, registers, widths and targets, including 0x18484 ->0x40000 and lookup ->0x19D10. A linker success alone is insufficient.
5. Confirm RAM NOBITS35152 at0x20004000, no BIN payload from it, and initialized data stays in the RO union. Inspect PT_LOAD file/memory sizes and physical addresses.
6. Reconstruct selected Flash payload independently and byte-compare against objcopy output. Validate min LMA0x8000, final span/length, every gap's known original provenance, exact carrier hashes and source/rebuilt byte proportions. Do not expect whole-BIN equality to prove semantic recovery.
7. Manifest must retain `target_ready=false`, `ota_verified=false`, `goal_complete=false`; mark ROM and full-table provider/ABI checks unknown and explicitly distinguish final static link placement from physical verification.

Reviewed primary evidence: existing `experiments/tsl9-lookup-domain-closure/{layout/closure.json,layout/runtime-known-memory.ld,src/target_runtime_ram_only.c,src/target_stack_address_r81.c,verify-native.ps1,audit-native.py}`, the actual R81 C memory ELF under `build/c/314eca1a9e964cb491b4a28a1d37889a/known-memory.o`, `analysis/round81/receipts/destination-c/{producer.json,strict-final-link.log}`, `analysis/round81/literal-evidence.json`, `analysis/round81/independent-reset-address-contract/contract.json`, and active `experiments/tsl9-contract-model/src/target_reset_fidelity.c`. Readelf was used only to inspect existing files; no target execution occurred.
