# Main initialization, register setup and eight-byte carriers

[繁體中文](README.md) · [C/C++](../../src/native/receive/main_runtime_family.c) · [Evidence](evidence.json) · [Summary](summary.json)

Six complete original functions add704B/241 instructions,verified as C11 and C++17.8E88/9958/9F12/9E84 resolve four old imports. Eight newly exposed dependencies change71 to75; these remain real undefined symbols,without stubs. The [inventory](next-providers.json) separates direct sites and PC-relative address references.

| Original range (exclusive end) | Confirmed static behavior |
| --- | --- |
| 8E88–9008 | Complete32B frame/S0/S1,ROM-table reads,initialization order and config byte7 low2-bit branch. First tuple:A0=0x2000B18C,A1=0,A2=2124; ROM semantics unknown. |
| 937E–93AA | Read a halfword from the9E84 return carrier,call9334,compare and store booleanGP+167. |
| 9958–99E8 | Preserve ISA DIVU,clock wordGP+108,16-bit truncation and halfword RMW. Store low16(clock/1000000−1) at0x40000428; tail93EE. |
| 9E5C–9E84 | Preserve272B frame/RA+268,eight-byte ROM tuple,then call unresolved9C0A withA0=0x08077B00/A1=SP. Physical storage writes unproved. |
| 9E84–9EA6 | Pass A0=SP,A1=0x08077B00,A2=8 to word[0x4004C]; return two local words inA0/A1. |
| 9F12–9F4C | ClearGP+169;if local byte1!=16 or byte4!=0,update those bytes and call9E5C; finally call937E. |

8614 has three address references;8C82 has one. Both remain unimplemented callback candidates. Constants19DEC/19DFC/1AB34 remain unowned. Contents at operand value0x08077B00 are absent from this BIN; ROM semantics are unknown. No VIN/key/configuration identity or observed copy/storage action is inferred. Timer-style register structure is an inference; physical MCU/peripheral/timing remains unproved.

Native code16808B+data674B:all17482B match officialID2966 bytes after original-address placement.108 C/H files,81 code units,164 comparisons/328 objects; all107 earlier sources and961 artifact records retained.955 direct transfers:882 measured targets,73 unimplemented references. Two additional providers only have address-load references,total75 UND.298 indirect transfers and356 potential returns do not prove complete CFG/reachability or execution.

Potential tool: offline comparison of eight-byte carriers and byte1/byte4 normalization across versions,with unknown fields preserved. Proposal only; no hardware backup/restore before ROM/storage contracts are proved. Next:eight exposed providers and three constant references. No firmware/HOST/ISA execution,hardware or network. Entry0/PT_LOAD0 diagnostic ELF is not flashable firmware. Publication remains held for unresolved historical privacy findings; no commit/push.
