# V4.1.60 Flash original source and register contracts

This review binds ID2966 Runtime SHA-256 `0ee64183…32fb667`, loaded at `0x8000`. It executes no firmware, CPU emulator or device operation; it performs no network request and creates no BIN. [繁體中文](readme.zh-TW.md)

Run `python inspect.py --check` for offline exact replay. Only optional recapture requires the pinned Windows radare2. Normal replay compares retained `r2-source.json` rows against the actual firmware and a separate bounded integer/CSR decoder.

| Original entry | Bytes | Original role | Encoded GPR destinations in body |
|---|---:|---|---|
| `9C0A` | 64 | Quarter-page wrapper | RA/SP/S0/S1/A0/A1, plus callees' effects |
| `18E90` | 8 | Status SW32 | A5 |
| `18E98` | 30 | Four ordered key SW32s | A3/A4/A5 |
| `18EB6` | 14 | Fresh control RMW setting bit15 | A3/A4/A5 |
| `18EC4` | 46 | Align, control/address writes and busy poll | A0/A3/A4/A5 |
| `18EF2` | 100 | 64 word transfers and busy polls | A0/A2/A3/A4/A5/A6 |

The six extents total **262 bytes / 99 instructions**. Actual section bytes, STT_FUNC symbols and sizes match the authoritative 691-allocation carrier. No older model address was transplanted as current proof. `source-proof.json` contains all decoded rows and 20 actual raw-byte negative controls. The semantic checks reject them before any firmware digest gate: CSR, frame slots, call target, key order, poll masks, access widths, source register, stride, loop and return.

`9C0A` allocates 32 bytes and stores S0/S1/RA/source A1 at offsets 24/20/28/12 in that order. It clears CSR `0x800` mask136 at `9C1A`, calls unlock, status49, erase, program and lock, then sets mask136 at `9C3C`. This is not prior-state restoration. It freshly reloads source A1 from `SP+12` at `9C30`, and freshly restores RA/S0/S1 at return. Retaining the pointer solely in an ordinary C local does not establish equivalence to those original observations.

Program entry A2 is not a length. `18F16` assigns256. The second poll's masked A5 is zero on exit and seeds the copy index. `18F1E` loads the source word, `18F26` stores the destination word, **two-byte C.ADDI** at `18F30` advances by4, and `18F32` stops at256. Normal completion therefore performs64 ordered word transfers at offsets0..252. RV32 address sums wrap modulo2^32; physical mapping, alignment faults and accessible memory remain unknown.

`contracts.json` records inputs, fresh effects and normal return residues. Wrapper A0 is the destination aligned down256, **not success code zero**. A1 is the fresh source pointer selected before programming; A2=256, A3=`0x8000`, A4=`0x40022000`, A5 is the final lock's fresh control word OR `0x8000`, and A6 retains the last source word. An ordinary C ABI or HOST callback cannot prove these physical register outputs: actual compiled instruction proof is required.

The retained `9D00` continuation first reads S0/S5 and then overwrites A5/A4/A3/A2 before consuming them. This bounded observation does not establish deadness at other direct or computed callers. Three earlier OTA-route, resident-callback and Flash-chain seals are checked member by member and reused without repeating their historical pipeline.

Original polls have no timeout or error-return branch. A permanently busy bit prevents subsequent effects, lock, CSR set and return. A bounded HOST provider must explicitly report unknown/nonreturn and preserve only the observed prefix; budget exhaustion is not an original firmware timeout. Conclusions require normal control flow and completed accesses. Pointwise interrupt behavior, resident ROM ABI, physical MCU, Flash geometry, write success, timing, recovery and OTA readiness remain unproved.

Native acceptance requires the individual 64/8/30/14/46/100-byte limits, actual per-function GPR destinations, fresh32-bit effects and poll ordering, five JAL targets, frame and CSR sequence. Whole-image section/symbol/alias/relocation and interior-entry checks remain separate integration gates. No apparent spare bytes or caller-clobbered registers are automatically available.
