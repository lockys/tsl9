# Original transport-framing contract

[繁體中文](original-contract.md) · [Complete JSON / 96 rows](original-contract.json) · [Prior instruction evidence](../queue-filter-2026-10-23/next-transport.json)

Official ID2966 V4.1.60 `[0x8A56,0x8B6E)` contains280 B /96 instructions; SHA256 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`. Fresh r2, the actual BIN and all96 retained rows agree. Raw branch/C.J/C.JALR/C.JR fields were checked independently of ESIL. JSON retains full firmware/tool hashes, recipe and per-region hashes.

The local CFG has96 nodes /101 edges, with every row syntactically reachable assuming opaque calls return to their encoded continuations. Path feasibility is not proved. Exits are `8ACA RET`, `8B50 JR T1`, and `8B6C RET`. The post-RET `8B52..8B6C` copy block returns to `8B0A` and must remain included. These are analysis cuts, not claims about original FUNC symbols.

| Range (exclusive end) | B | i | Block |
|---|---:|---:|---|
| `0x8A56`–`0x8A5E` | 8 | 2 | entry_guard |
| `0x8A5E`–`0x8A7A` | 28 | 12 | frame_capture_and_first_channel_match |
| `0x8A7A`–`0x8A90` | 22 | 7 | first_admission_call |
| `0x8A90`–`0x8A96` | 6 | 2 | first_admission_result |
| `0x8A96`–`0x8AB6` | 32 | 10 | second_admission_call |
| `0x8AB6`–`0x8ABE` | 8 | 3 | second_admission_result |
| `0x8ABE`–`0x8ACC` | 14 | 7 | ordinary_restore |
| `0x8ACC`–`0x8ACE` | 2 | 1 | select_bank_zero |
| `0x8ACE`–`0x8B0A` | 60 | 18 | header_and_checksum_seed |
| `0x8B0A`–`0x8B14` | 10 | 3 | copy_test |
| `0x8B14`–`0x8B52` | 62 | 22 | checksum_metadata_restore_tail |
| `0x8B52`–`0x8B6C` | 26 | 8 | cold_copy_body |
| `0x8B6C`–`0x8B6E` | 2 | 1 | unframed_reject_return |

The unsigned A3>1039 guard precedes the frame. Rejection leaves A0/SP unchanged in this body's instructions. The accepted path creates a32 B frame, saves S0/S1/S2/S3/RA, then captures S2=A0, S0=A3, S1=A2 and S3=A1.

Fresh halfwords GP+150/154 are compared with the full32-bit channel and FFFE is excluded. Each admission at `8A8E`/`8AB4` freshly loads [4013C] into A5 and C.JALRs with RA=`8A90`/`8AB6`; A0==1 selects bank0/1. The second port's A2/A3 can be earlier port residues: they are not reloaded from S1/S0. Subsequent GP, S0..S3, SP and memory accesses use then-live values. There is no ordinary C callee-preservation assumption. The entry length guard is not repeated after admission; the actual loop predicate is `u16(index)<u32(S0)`. Post-call bounds, termination and pointer validity are unproved.

At its original placement the PC-relative base is2000B18C, bank stride1062 and D=base+bank*1062+6. Store order is SH magic7F55, SB low length, SB high length, SB command. The loop freshly reads S1+index, writes D+5+index, and accumulates/masks checksum to255 each iteration. The checksum is stored at D+5+L. Metadata becomes SH[bankbase+2]=u16(L+6), SH[bankbase+4]=0. Conditional on normal loop completion, checksum is `u8(command+u8(L)+(L>>8)+sum(payload bytes))`. These are byte equations, without a named physical protocol or successful-delivery proof.

The tail restores RA/S1/S2/S3 before metadata writes and restores S0 only at `8B40`. A fresh LW[40050] loads T1, A0=fresh LBU[GP+148+4*bank], A1=1, SP+=32, then `8B50 C.JR T1` does not write RA. Ordinary return leaves A0 residue; there is no uniform success result or CSR instruction.

After the caller filter's opaque port at8356,8358/835C/8360 use then-live S1+2/S0+2/SP+4.832C captures S4 before832E checks DLC, so filter nonzero is not a successful-delivery counter.

Readable C can express comparisons, bank arithmetic, bytes/checksum and the copy loop. Explicit architecture ports must retain frame/fresh GP/S-register/SP observations, two admissions, PC-relative base and true tail control. Useful future offline diagnostics are snapshot-backed bounds/alias/wrap checks, format/checksum checks on explicitly supplied records, and separation of filter result from delivery evidence. They must not invent providers, nonaliasing or seat/DND attribution.

No target, ISA, ESIL, MMIO, hardware or network execution; no firmware BIN or flashing. Resident ABI, IRQ/fault effects, physical ownership, global incoming references and delivery/hardware results remain unknown. `firmware_ready=false`.

The candidate `experiments/tsl9-transport-frame/src/transport_frame.v1.c` was read at SHA256 `6dad92397a447d83103fbddbfda661117089968967cba4676473785e92ba5f13`. A concrete mismatch was found: both v1 admission loads use0x0040013C, whereas the actual BIN computes0x0004013C. The earlier no-mismatch conclusion is withdrawn. Its13 private regions additionally cut at8A90/8AB6 for post-call imports. This is source reading only; flags, IR, all96 native instructions, spills/frames, relocations and whole-code equality still require independent measurement.

Address correction: raw LUI`b7070400` produces0x00040000; raw LW`83a7c713` adds316=0x13C, yielding0x0004013C. Earlier summaries incorrectly stated0x0040013C. The original BIN did not change. The tail word remains0x00040050. JSON records both admission derivations and the tail derivation.
