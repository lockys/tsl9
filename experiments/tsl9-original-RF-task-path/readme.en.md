# RF task,sampling comparison and hopping shutdown

[繁體中文](README.md) · [Initialization/polling](../tsl9-original-RF-reset-path/readme.en.md) · [Send/retry](../tsl9-original-RF-tx-path/readme.en.md)

Add **1,586 bytes /576 instructions in seven complete candidate bodies**,supplying three actual RF-task dependencies plus required helpers/a registered callback. C/C++ retains original register context and assembly ports;these are not ordinary host-callable APIs.

| Body | Original range,end exclusive | Bytes /own frame |
| --- | --- | ---: |
| Sampling monitor | 0x43EDC..0x43F46 | 106 /16 |
| RF_FrequencyHoppingShut | 0x6575A..0x657D8 | 126 /16 |
| RF task state handler | 0x657D8..0x65920 | 328 /48 |
| Internal RF helper | 0x64794..0x6498A | 502 /64 |
| Indexed word setter | 0x43B28..0x43B3E | 22 /0 |
| Registered callback | 0x65DE6..0x65F94 | 430 /32 |
| RAM byte comparison | 0x20000442..0x2000048A | 72 /0 |

## Actual behavior and limits

RF task0x65920 event4/8/16 paths call0x657D8/0x6575A/0x43EDC. Event8 also requires context byte0x2000356C&4. Higher-priority event paths can return first;the presence of a bit alone does not guarantee its call. After sampling,state byte0x2000351B==8 conditionally schedules event16 with raw time1600. Units and liveness remain unproved.

Body0x43EDC reads callbacks at candidate library configuration0x200031EC+44/+48,matching primary header fields tsCB/rcCB. A null tsCB returns before frame allocation. Old halfword0x200031A4==0 skips comparison actions. Preserve the exact remaining algebra:

```text
hi = low16(max_u32(sample, old))
lo = low16(min_u32(old, sample))
delta32 = hi - lo
action iff int32(delta32) > 20
```

Only a callback honoring the primary uint16_t return ABI permits interpreting this as absolute difference>20. Celsius units are unproved. Actions are optional rcCB,common reset,then storing sample low16,conditional on normal returns,register preservation and valid memory. Physical callback values/effects are unobserved.

The primary header/candidate table maps index116/slot0x40204 to RF_FrequencyHoppingShut. It stops task events8/4,then uses raw status34 or lower-priority36 through callback word0x20003550 and clears context flags. It releases its16-byte frame before tailing to0x43B28 withA0=0,A1=2,writing indexed word0x200031D0. Preserve the tail rather than an ordinary call retaining the frame. The setter writes only for unsigned index<=4;physical array capacity/ownership remain unproved.

The helper's callback literal0x65DE6 has a complete selected body. **Five opaque callback calls** remain,including two reads of clock-like callback word0x200031E0. The RAM helper returns1 on null/zero-length or matching-byte paths and0 on mismatch,while preserving hardware-word0x4002420C save/clear/FENCE.I/restore. This proves neither IRQ masking,atomicity nor caller bounds.

## Verification

Actual C11/C++17 CODE and ABI objects are identical. All original-context bytes,whole CFG own frames,nine far call pairs,52 primary Xwchc positive vectors and38 actual ports pass. All16 explicit imports have real prior providers. The104 FUNC regions are compiler fragments,not logical functions.

The unique composition has **20,112 CODE+256 DATA bytes /6,906 instructions**,1,298 FUNC regions and977 relocations. Genuine named dependencies decrease from **14 to11**,without new ones. Every input byte/symbol/relocation and source-PC uniqueness is verified.

The actual2,218-section composition exceeds the old reader's exclusive2,048 ceiling. A separate bounded v6 reader uses an exclusive4,096 ceiling;only that finite ceiling and explanatory documentation change. All other structural/file-extent checks remain. An independent parser compares every section field/byte,symbol and relocation;all records of the actual2,040-section parent equal v5. The actual larger object reproduces the old limit failure without synthetic inputs. Original v5 remains unchanged.

An earlier ABI trial failed because declarations were missing. Current native-v2 directly includes the pinned primary header and checks32-byte RF config,64-byte library config,tsCB+44/rcCB+48 and uint16_t/void callback signatures. Failed native-v1 and partial composition-v1 are retained locally. Current evidence uses native-v2/audit-v2/composition-v2.

Formal APP stays159 C/H files and95.54% byte coverage,not functional completion. No APP integration,newBIN,target/model execution or hardware access. The4-byte startup source gap,ROM/RAM/ISA/IRQ,whole-program stack/aliasing,callbacks,Flash/OTA remain open. **Usable replacement firmware has not been successfully reconstructed.** Sampling/calibration provenance and hopping-state diagnostics remain an unimplemented observation-only UI candidate.

[C/C++](original_RF_task_path.c) · [Original instructions](evidence-v1.json) · [Audit](audit-result-v2.json) · [Summary](summary.json)

## Reproduce

Provide pinned local inputs,prior native artifacts,Windows NDK LLVM and official headers required by the trap audit. Missing inputs are not downloaded.

```sh
python experiments/tsl9-original-RF-task-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-task-path/build/native-v2
python experiments/tsl9-original-RF-task-path/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

For new artifacts replace `--replay` with `--trial`,and add `--link-trial` to the second command;names must be unused. Cross-platform compilation is unverified.
