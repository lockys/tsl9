# Original incoming parser and typed function-pointer data

[繁體中文](README.md) · [C/C++](../../src/native/receive/incoming_protocol.c) · [Evidence](evidence.json) · [Summary](summary.json)

Three complete85C8/888C/8B90 functions add776B/262 instructions plus40B of real C readonly prefixes. Both C11/C++17 match original-address bytes. Three nonnull19DE0/19DFC pointers now reference reconstructed code. Two downstream handlers13E0E/14056 remain unimplemented;72 UND becomes74.

| Original range (exclusive end) | Confirmed static behavior |
| --- | --- |
| 85C8–8614 | Compare GP+150/154 halfwords; preserve low16 parameter predicate and original ROM event tuple. Units unproved. |
| 888C–8A56 | Preserve headerbit0x20,type2,0x2902 and handle checks. Valid parser path uses64B frame with all post-first-RET states. |
| 8B90–8C82 | Original event values2/3/4,subtypes5/6,GP fields,0xFFFE clear value and13E0E call. |

Parser keeps55/7F sync,command byte,two-byte big-endian length,max1040-byte body and low8 additive check.14056 is called only after comparison succeeds. Invalid/oversized/checksum/reset paths and raw time-delta threshold299 are retained; units remain unknown. No packets,firmware,HOST model or ISA emulator were executed; no verification condition was changed.

| Typed C prefix | Bytes | Original measured content |
| --- | --- | --- |
| 19DE0 | 12 | 8B90,NULL,85C8 pointer slots |
| 19DFC | 12 | NULL,888C,NULL pointer slots |
| 19DEC | 13 | Original fixed carrier prefix |
| 1AB34 | 3 | Original byte lookup prefix |

All40B come from actual C objects. Three real R_RISCV_32 references preserve nonnull pointers. The unknown19DF9–19DFC gap is not filled. All four known targets now have owners; complete ROM structure extents,types/ABI and observed registration remain unproved.199E2/19B16 show lower-level startup setup; the earlier assumed direct registration link was not established. This milestone uses the actual data pointers as evidence.

Code18656B+data714B:all19370B match officialID2966 after native original-address placement.110 C/H files,83 code units,168 comparisons/336 objects; all109 earlier sources and985 artifact records retained.1055 direct transfers:981 measured/74 reference-only.339 indirect transfers and395 potential returns do not prove full CFG or execution.

Potential addition: offline length,sum and reset diagnostics,proposal only. Next:14056 command dispatch/13E0E state handling and ROM/memory contracts. No hardware or network. Entry0/PT_LOAD0 diagnostic ELF remains nonflashable. Historical privacy findings still hold publication; no commit/push.
