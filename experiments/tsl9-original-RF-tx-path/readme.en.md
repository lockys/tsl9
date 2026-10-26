# Actual APP RF send/retry and candidate execution layer

[繁體中文](README.md) · [Unique CODE composition](../tsl9-sdk-unique-code-ownership/readme.en.md) · [RF initialization](../tsl9-original-RF-bridge/readme.en.md)

Add **1,778 bytes /620 instructions in eight complete candidate SDK bodies**, compiled as original-register-context C/assembly in C11 and C++17. They are not ordinary host-callable APIs.

| Body | Original range, end exclusive | Bytes /own frame |
| --- | --- | ---: |
| RF_Tx | 0x64CEC..0x64F04 | 536 /48 |
| RF_Shut | 0x656C6..0x6575A | 148 /16 |
| RF_SetChannel | 0x65F94..0x66056 | 194 /0 |
| Basic TX callback | 0x64422..0x6448E | 108 /16 |
| Auto TX callback | 0x6448E..0x645DC | 334 /16 |
| ACK-phase callback | 0x645DC..0x646A8 | 204 /32 |
| Clock/hop-like helper | RAM0x20002D4C..0x20002DF2 | 166 /32 |
| Index-like helper | RAM0x20002C50..0x20002CA8 | 88 /0 |

RAM sources follow the pinned SDK copy mapping. Names describe candidate behavior; time units, physical chip identity and full protocol remain unproved.

## Direct APP evidence

Original sender0x1753A, RF task0x17476, completion0x173EE and retry0x17442 total **430 bytes /147 instructions**. Every byte matches both the official APP BIN and existing compiled original-address diagnostic ELF. All19 PC-relative data addresses are independently recomputed from actual instruction fields.

- Retry byte0x2000C7A8 starts at50. Retry computes `low8(previous-1)`; nonzero tails to timer(event1,raw time2),zero tails to completion withA0=1. Timer units and whole-process liveness are unproved.
- Byte0x2000C7A9 is both a nonzero sender rejection guard and the transmit length. The sender stores `low8(caller_A4+3)` and copies caller_A4 bytes from caller_A3 to0x2000C7AD. There is no local sender length limit; all caller bounds remain unknown.
- The RF task calls RF_Shut slot0x401D0 before RF_Tx slot0x401CC,with buffer0x2000C7AA,length from that byte,A2=A3=255. It immediately overwrites returnedA0 with the event mask; this local path does not consume the RF_Tx status.
- Completion stops event2,clears retry/length and clears optional callback word0x2000C7A4 before releasing its frame and tailing through it. Preserve the opaque tail rather than an ordinary C call retaining its frame. Callback effects remain open.

The sender also invokes SetChannel slot0x40200,starts event2 with raw time320,and sets event1. The primary header/candidate table map these three RF slots to the selected complete bodies. Installed ROM identity remains unproved.

`N<=252` is only a sufficient numeric condition for representingN+3 in one byte;13+252<=268 also fits the constructor-cleared interval. **Neither is an existing runtime guard or proof of a physical maximum payload.**

## Candidate SDK and verification

Retain reachable arms after returns and multiple cleanup paths. RF_SetChannel directly tails at0x65FEA to existing0x6434A. Numeric callbacks0x64422/0x6448E/0x645DC have actual complete bodies. **Four opaque transfers** remain. The clock-like word0x200031E0 used by TX and the RAM helper must not be confused with status callback word0x20003550.

C/C++ objects are identical. All1,778 original-context bytes,whole CFG own frames,52 official Xwchc positive vectors,40 actual ports and two ELF readers pass. All12 named imports have real prior providers. The unique composition has **14,436 CODE+256 DATA bytes /5,032 instructions**,1,169 FUNC regions and878 relocations,with **19 genuine unavailable named dependencies**. Region counts are not logical function counts. Every input byte/symbol/relocation and original-PC ownership is verified.

Formal APP remains95.54% byte coverage and159 C/H files,not functional completion. No APP integration,newBIN,target/model execution or hardware access. The4-byte startup source gap,ROM/RAM/ISA/IRQ,stack/aliasing,callbacks,Flash andOTA remain open. **Usable replacement firmware has not been successfully reconstructed.** Send-length/retry/callback diagnostics remain an unimplemented UI candidate.

[C/C++](original_RF_tx_path.c) · [Original instructions](evidence-v1.json) · [Audit](audit-result-v1.json) · [Summary](summary.json)

## Reproduce

Provide pinned local inputs,prior native artifacts,Windows NDK LLVM and official headers required by the trap audit. Missing inputs are not downloaded.

```sh
python experiments/tsl9-original-RF-tx-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-tx-path/build/native-v1
python experiments/tsl9-original-RF-tx-path/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

For fresh artifacts replace `--replay` with `--trial`,and add `--link-trial` to the second command;names must be unused. Cross-platform compilation is unverified.
