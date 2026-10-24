# OTA finalizer dependencies: record checks and module state

[繁體中文](README.md) · [C/C++](../../src/native/receive/ota_finalizers.c) · [Original instructions](evidence.json) · [Summary](summary.json)

Two complete functions add182B/69 instructions,22 private regions and14 control relocations. All downstream functions already exist; genuine missing providers73→71 with no new imports. C11/C++17 and original-address placement pass.

| Range | Confirmed static behavior |
| --- | --- |
| 9EA6–9EE0 |32B frame,reads the two-word/eight-byte record returned by9E84,compares its byte4 with the full32-bit input,and writes low8(input) through9E5C on mismatch. At most five writes. Return0 requires an observed match; the fifth write returns1 without a final reread. |
| 16E0C–16E88 |Input bits0/1 select writes16/1 to0x40010814,calls16896(192),then writes17 to0x40010810. Polls16994(input,14)&0xE0==0x80. Unsigned tick difference>2 returns1; matching state returns0. Tick units and physical effects remain unproved. |

Original9EE0 calls9EA6(1),does not branch on its result,and tail-jumps99E8(0). Reset-request flow may therefore continue without final flag-readback evidence. This does not prove a failed physical write; E or entering reset flow does not prove persistence either.

Correction to the preceding report:8E66 jumps directly to8E4A JR T1,skipping8E48 SP+=16. The previous stack-imbalance claim counted a skipped instruction and was incorrect. Original instructions and reconstructed C/C++ remain unchanged. Three preceding public reports were corrected; originals are retained locally,and the earlier final receipt remains a historical snapshot. Complete caller/ROM ABI is still unproved.

Current113 C/H files and86 code units pass174 comparisons/348 objects including independent pointer data. Previous112 sources and1021 artifact records are preserved. The component contains20224B code+714B data; all20938B match the official ID2966 BIN at native original addresses.71 real providers remain explicit,no stubs or ABS functions.

Static flow covers7033 instructions,1160 direct transfers(1089 measured/71 reference-only),6487 ordinary next positions without gaps,and431 potential call-return positions.363 register-indirect transfers,10MRET and1EBREAK remain short of a complete CFG or physical proof. Diagnostic ELF entry0/PT_LOAD0 is not flashable.

Next: main initialization131C2/12D92 and ROM/BOOT/APP mapping. A proposed OTA completion-evidence display would separate reply,page readback,flag readback,reset and functionality observations; it is not implemented and changes no original checks. No target/HOST-model/ISA execution,hardware or network actions occurred. Historical privacy findings keep commit/push held.
