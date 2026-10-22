# Independent native NV write/timer object review

[Traditional Chinese](readme.zh-TW.md)

This review supports only a conditional normal access/call/A0-result projection of the new C/C++ write callback and timer. Full original register ABI, fault/IRQ equivalence, in-place replacement, Flash success and physical compatibility remain unproved. No native/MMIO/ISA execution, unchanged HOST suite, linking or new firmware BIN was performed.

`source.py` independently decodes six retained original ranges, 294 bytes / 115 instructions, and compares them with the actual ID2966 firmware. It also agrees with the separately sealed source review. `check.py` reads actual ELF bytes, all LLVM disassembly operands and LLVM IR. Producer replay is not its verdict.

| Actual global function | Bytes | Instructions |
| --- | ---: | ---: |
| status 18E90 | 8 | 3 |
| unlock 18E98 | 30 | 10 |
| lock 18EB6 | 14 | 6 |
| erase 18EC4 | 46 | 19 |
| program 18EF2 | 100 | 38 |
| unused quarter 9C0A | 64 | 23 |
| new timer 19764 | 60 | 23 |
| new write 197BE | 72 | 26 |

Both languages retain eight genuine definitions totaling 394 bytes / 148 instructions. All eight allocations are fully decoded: UND 0, RELA 10, global ABS 0. Five CALL_PLT relocations belong to actual typed C calls in the new writer; five JAL relocations belong to the retained quarter. Every relocation names a genuine defined provider, with no stub, ABS provider or omitted unused function. Source, tools, Python and compiler stdint are hashed. The complete MD closure is the new C/header, three original Flash files and stdint. One ordinary first profile is used without adaptive flags.

The new writer calls unlock(destination), erase(destination), program(destination, source), lock(program A0), timer(1), then returns A0=0. Input A1 is unused. Original program entry A2 also contains the source pointer, but the original callee defines count=256 before reading A2. The two-argument C surface therefore describes the bounded effect projection rather than a recovered full prototype or complete entry state. Program still interleaves 64 fresh source-word reads, destination-word writes and polls.

Original write uses a 32-byte frame, saves the source at entrySP-20 and reloads it after erase. New write uses 16 bytes, keeps source in S0 and destination in S1, and saves/restores RA/S0/S1. It writes incoming S1 at entrySP-12 and does not reproduce the old source slot. Normal projection requires valid private frames, no adverse alias/intervening writes, and unobserved private residue. Original code restores RA/S0 before zeroing A0; new code zeros A0 first. Fault prefixes differ.

Timer has twelve minimum fresh volatile effects: STATUS+4 read/write clearing bit0; GP+382 byte read; low32 input-times-byte write to CMP+16; zero to CNT+20; fresh CTRL+0 read/write OR16; another fresh read/write OR33; repeated STATUS+4 reads until bit0 becomes set; fresh CTRL+0 read/write clearing bit0. The GP port is a real `mv`, without writing GP. Timer units, physical duration and termination are unproved.

Original timer preserves A0/A1 and exits with A2=product, A3=0, A4=final CTRL&~1, A5=E000F000. New timer is frameless and writes only A1/A2: A0 is preserved, A1=E000F000, A2=final CTRL&~1, while A3/A4/A5 retain their incoming values. Composed new write therefore leaves A3=8000, A4=40022000, A5=last fresh lockCTRL|8000 and A6=the final source word. These confirmed differences keep full ABI false.

Unused quarter's ASM call constraints omit the new ordinary unlock/erase A1 writes. The checker mechanically verifies both omissions. This exact quarter saves source before the calls, reloads after erase and has no intervening encoded A1 read, so no counterexample was observed in that bounded machine path. This does not repair its generic ASM/compiler contract or admit its full ABI. Sealed old source is unchanged.

Each language rejects twelve actual negatives: eight valid single-field raw operand mutations cover STATUS/GP offsets, OR33, poll target, source capture, fixed count, stride and call link register. Four IR mutations cover program-to-lock A0, source argument, timer(1) and the full input product. There is no new ROM slot or word-count shift in this scope; no inapplicable control is invented.

```sh
python3 check.py --project-root ROOT
python3 check.py --project-root ROOT --folder ROOT/experiments/tsl9-nv-write-callback/build/native-v1/c --receipt NEW.json
python3 check.py --project-root ROOT --replay NEW.json
python3 check.py --project-root ROOT --firmware ORIGINAL.bin
```

Default mode checks metadata and retained source without reading native objects. Actual folder review writes only a new receipt; replay reads that artifact again without mutation. Firmware source mode can also write a new receipt and makes no claim about other images. Source/native-reader contexts resolve from D/P and 199 existing external dependency hashes match in each. Two canonical reader aliases are confirmed absent: `analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py` and `analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py`. Parent will deliver these exact original hashes and sibling hierarchy, preserving old files, producer seal and objects. `delivery-dependencies.json` records the requirement; this seal does not claim alias delivery or fresh D/P compilation. Python/POSIX sh source portability is not cross-OS execution evidence. The previously denied Git Bash was not retried; sh runtime remains unverified.

Required normal premises include successful accesses, valid GP/pointers/private frames, finite polls, no asynchronous modification/observation and unchanged genuine providers. `machine-findings.json` records precise differences. Previous seals and existing candidate images remain unchanged.
