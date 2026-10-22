# ADC configuration candidate: shared C/C++ core and native static outputs

[繁體中文](readme.zh-TW.md) · [English](readme.en.md)

The supplied V4.1.60 firmware was actually read and the **88B / 37 instructions at 0x1892E..0x18986** re-decoded before reconstructing readable C11/C++17. This is a numeric-address memory-effect projection. The ADC name does not establish physical hardware identity or flashability.

Shared API: `ml_result tsl9_adc_config_io(ml_io*,uint32_t base,uint32_t config)`. It ordinarily includes sealed memory_leaves.h/io.h and uses exactly three real typed ports: read32, read8, write32. Normal completion returns {CONTINUE,base,1}; a stopped callback returns {flow,0,0} without cleanup. Original A0 remains base; the u32 return is an explicit reconstruction interface projection, not a recovered original C prototype.

## Exact effect order

Each field is freshly read at its original point; the entire config is not prefetched. Offsets below are decimal.

| Group | Reads in source order | Write |
| --- | --- | --- |
| First | WORD(base+4), WORD(config+24), WORD(config), WORD(config+28), WORD(config+4) | WORD(base+4) |
| Second | WORD(base+8), WORD(config+12), WORD(config+16), WORD(config+8) | WORD(base+8) |
| Third | WORD(base+44), BYTE(config+20) | WORD(base+44) |

All fourteen effect addresses and arithmetic wrap as uint32_t:

```c
new4 = (old4 & 0xe0f0feffu) | cfg24 | cfg0 | cfg28 | (cfg4 << 8);
new8 = (old8 & 0xfff1f7fdu) | cfg12 | cfg16 | (cfg8 << 1);
new44 = (old44 & 0xff0fffffu) | (((cfgByte20 - 1u) & 255u) << 20);
```

Config WORDs retain all 32 bits; no inferred field narrowing is added. Config+20 is a BYTE: subtract one and mask 255 before shifting; zero becomes 255 and can affect bits 20..27. Numeric zero base/config does not acquire a new null guard. HOST diagnostic budgets bound synthetic tests only; native ports omit that artificial limit.

## Actual validation

C and C++ each pass **80 synthetic cases / 6864 checks**, covering high config bits, byte20={0,1,128,255}, base/config address wrap, numeric zero, config=base-8 aliasing, callback memory mutation at every boundary, fourteen stop points times HALT/TRANSFER/UNKNOWN, and budgets0..13. Each language also compiles three actual semantic controls rejected by assertions: narrowing a shifted WORD, omitting the BYTE decrement mask, and reading the wrong fresh WORD address. Tests use a synthetic map and never cast numeric addresses to HOST pointers. No previous HOST matrix was rerun.

native.c ordinarily includes the same core, with actual volatile-address ports. Public `uint32_t tsl9_adc_config_1892e(uint32_t base,uint32_t config)` uses the existing justified always_inline and A0/A1 empty-asm bridge. Fixed NDK 27.1, -Oz, rv32imac_zicsr_zifencei, ilp32 and no machine outliner remain; there is no flag sweep.

| Genuine global FUNC | Bytes / instructions | Note |
| --- | ---: | --- |
| tsl9_adc_config_1892e | 102 / 38 | Two arguments; no context/sret, frame or call |
| tsl9_adc_config_io | 128 / 44 | Unselected genuine context/sret core |
| ml_port_read32 | 8 / 4 | Unselected genuine volatile port |
| ml_port_write32 | 6 / 3 | Unselected genuine volatile port |
| ml_port_read8 | 10 / 4 | Unselected genuine volatile port |

Complete ET_REL: **254B / 93 instructions, five global FUNCs, UND=0, RELA=0, no ABS provider**. No linker removal of the other four functions is assumed. C/C++ bytes match for all five functions. Public IR retains ten volatile WORD reads, one BYTE read and three WORD writes in exact source order.

The public native function writes A2/A3/A4/A5/A6/A7; the original writes A3/A4/A5 only. Thus **A2/A6/A7 are additional writes**; normal scratch liveouts and fault/asynchronous prefixes cannot be equated. 102B exceeds the original 88B extent by 14B. Full ABI, placement and installed-provider proof remain false.

**Never execute native.c on HOST: it contains real volatile MMIO.** Only synthetic HOST executables run. Native outputs receive compilation/static readback only; no RV32/ISA/MMIO/hardware execution, native-object link, objcopy, BIN or flashing occurs.

## Running and evidence

```sh
sh experiments/tsl9-adc-config/verify.sh --project-root "$PWD" --tool-dir LLVM
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE supports workspace apk-analysis/tsl9-v4160-adc-config-2026-10-22 and delivered analysis/v4160-adc-config-2026-10-22. Fresh --build-root must be create-only beneath model/build; omission uses UUID. Both C/C++ archives are produced. Default check reads source/metadata only; explicit receipts inspect actual HOST executable, mutant sources, native ELF, complete IR/MD/disassembly without recompilation or execution. Only provenance or check --firmware rereads original firmware and the finite instruction decoder; neither simulates a CPU.

Current W archives: build/verified-v1/{c,cpp}/verification.json. Actual compiler hashes, HOST-format admission, compiler resource stdint.h, six actual native MD inputs, all logs and complete inventories are retained. Python/sh sources are portable; native results admit only fixed Windows NDK hashes. sh runtime remains unverified: no retry followed the previous MSYS launch denial. Newly authored source/docs use LF, exactly one EOF newline and Git-style whitespace checks. Actual raw compiler logs retain any CRLF as evidence.

Initial build/first raw outputs and initial-probe-snapshot.py remain historical. Read-only replay exposed a tuple/list JSON representation mismatch; only that probe serialization was repaired, then identical source/flags/tests rebuilt verified-v1. Both current explicit read-only replays pass. Old initial receipts are not current-probe replay evidence.
