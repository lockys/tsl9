# Flash program entry ordering and ABI review

Final C11/C++17 program helpers are **100 bytes /38 static instructions**, with admitted normal return contracts, six-function components and five known interior loop roles. This does not prove complete original role identity, pointwise interrupt behavior or hardware readiness. [繁體中文](readme.zh-TW.md)

The original is ID2966 Runtime SHA-256 `0ee64183…32fb667`, program range `18EF2..18F56`. The sealed prior94-byte native body has37 instructions. Its exact reduction removed two4-byte base LUIs at original `18F08`/`18F12` and added one2-byte `LI A5,0`: `100−8+2=94`, `38−2+1=37`. Relocating the4-byte A0 alignment ANDI contributed zero bytes to that gap.

| Actual artifact | Bytes/instructions | First control read / alignment / first control write offsets |
|---|---|---|
| Original | 100/38 | `+4 / +8 / +E` |
| Prior native | 94/37 | `+4 / +18 / +A` |
| First fixed-A0 diagnostic | 94/37 | `+8 / +4 / +E`, alignment precedes read |
| Restored-base diagnostic | 102/39 | `+4 / +6 / +E`, exceeds extent by2 |
| Final natural100 | 100/38 | `+4 / +6 / +E` |

The final body restores two source-site base materializations and fixes initial masked poll results in A5. Actual compiled bytes reuse the second poll's zero A5 as the index, removing the explicit zero instruction: `94+8−2=100`. No padding or flag search creates this result. Static instruction count is not execution step count; original busy polls remain unbounded.

Final A0 remains input D before the first control read, aligns after that read completes and before the first control write. The first diagnostic aligned before the read and failed this observation; it is not the final solution. The prior94-byte helper deferred alignment past both initial polls. `program.py` checks the entire100-byte pattern, read/alignment/write order, encoded destinations,64 word transfers and normal outputs. IR checks bind8/4 static volatile i32 load/store sites and fixed-register bridges.

Scratch differences remain. Original first control load/RMW uses A5; final uses A2. Before the first write, original A2 is its entry value and A5 is fresh control OR `0x10000`; final A2 holds that RMW and A5 its entry value. Initial polls now both use A5, but final A2 retains the RMW until count256 replaces it. Matching normal A0..A6 outputs does not prove complete fault/nonreturn/asynchronous GPR prefixes.

The authoritative original691-allocation carrier has five interior symbol offsets `+10/+1A/+28/+38/+52`, all retained as numeric branch/copy roles. Seven relevant RELAs are five self-branches and two external entry calls at `9C34`/`197D8`. No admitted external interior RELA appears in that bounded set; computed incoming entries are not excluded.

Equal length/count still does not preserve all boundaries. Original `+8` starts ANDI; the new ANDI starts `+6` and spans it. New `+A` replaces that boundary. Mask-LUI/alignment order and scratch roles differ. Original local names, global entry aliases and `$d`/`$x` metadata do not automatically survive compilation.100 bytes closes the prior6-byte unowned tail issue only; full carrier/role integration remains open.

Each language rejects **12 actual machine-byte counterexamples** and **3 uncompiled IR transcript counterexamples**. Two remain100 bytes while moving alignment before the first read or after the first write, proving size alone insufficient. Five unchanged functions use immutable earlier full-pattern gates. Actual six objects/IR and original-entry component ELF/JAL fixups are reviewed without RV32 execution, emulation, network, hardware or BIN creation.

Run `python replay.py --check`. Optional `--context-json` accepts `project_root`, `prior_build`, `firmware`, `source_dir`, `parser`, mode-indexed `build_roots`; only input locations and historical location labels change. `variants.json` and `original-roles.json` retain actual diagnostic/original-metadata observations; locally retained diagnostic bytes are rechecked. Whole image, unknown interior entries, physical MCU/Flash geometry, programming success and OTA readiness remain unproved.
