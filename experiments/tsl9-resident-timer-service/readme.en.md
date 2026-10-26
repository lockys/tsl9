# Timer-list service candidate C/C++

[繁體中文](README.md) · [Actual main scheduler](../tsl9-resident-scheduler/readme.en.md) · [Queue/events](../tsl9-resident-message-queue/readme.en.md)

Scheduler call0x20000872 targets0x200004FA. The complete **288 bytes/103 instructions** at0x200004FA..0x2000061A are reconstructed. The following0x2000061A is another real entry and is excluded. **This is a public SDK V1.31 candidate;installed ROM identity remains unproved.**

[C/C++ source](resident_timer_service.c):32 positive FUNC regions and24 relocations. Actual C11/C++17 objects are identical;every byte matches after original-address encoding. Three conditional Xwchc ports are checked against primary definitions and28 official vectors. The existing import name tsl9_candidate_external_ram_200004fa is retained and resolved by a real body,without alias or stub.

## Observed flow

| Timer-node field | Observed offset |
| --- | ---: |
| Task byte/event halfword | 0/2 |
| Interval/deadline/next word | 4/8/12 |

- Traverse the list at0x200031E8. Zero-event nodes are unlinked and passed to the real heap-free provider. This supplies the deferred collection path after tmos_stop_task clears an event. Collection occurs only when the service runs;timing and list termination are not guaranteed.
- Nonzero-event paths call the clock pointer at0x200031E0 without an internal null guard. The known scheduler caller checks it beforehand,but pointer stability remains required. Clock units,range and side effects are unproved.
- Using runtime word M at0x20003238,unsigned elapsed is `now>=deadline ? now-deadline : M-deadline+now`. Elapsed≤29999999 takes the due path and calls the real event setter. **Its return value is ignored;successful enqueueing is not proved.**
- A due zero-interval node is freed. Otherwise add interval to a freshly read deadline once,and subtract M once if the sum wraps32 bits or is≥M. **No general modulo or multi-period catch-up is substituted.** No seconds/milliseconds conversion is asserted.
- Future-delay cache0x200031AC is reduced only on the nonnull-idleCB path. A nonempty traversal ends with `cache<=1 ?0:cache-1`. An initially empty list returns without this post-pass.

Its own48-byte frame balances at the shared return. Selected main+timer own frames total80 bytes,**excluding clock/other callees,reentry and IRQ stack**. Valid nodes of at least16 bytes,stable acyclic lists,ownership and normal callee returns remain assumptions.

## Actual partial composition

With the preceding2750-byte candidate,the actual nonloadable C/C++ ET_REL objects contain **3038 bytes/1074 instructions**,279 positive FUNC regions and205 relocations. Real timer,heap-free and event-set bodies resolve three cross-input imports. Every input byte,symbol and relocation is retained.

RAM0x2000061A/0x20002610 and Flash0x63DD0 remain unresolved,as does the clock callback contract. The previous4-byte startup source gap is preserved. No APP integration or new BIN is provided. Physical RAM/ROM/ISA,IRQ,stack,Flash and OTA remain open. APP byte coverage stays **95.54%**.

Evidence: [audit-result-v1.json](audit-result-v1.json),[summary.json](summary.json),[original instructions](evidence-v1.json). Timer lateness,clock-range and deferred-cancellation diagnostics are possible additions,not implemented features.

## Reproduce

Provide the original APP,SDK/header/instruction references and retained artifacts required by [spec-v1.json](spec-v1.json)/[evidence-v1.json](evidence-v1.json) and the audit. Original SDK inputs and native artifacts are not included in this commit. Nothing downloads them automatically. From the project root using the hash-pinned Windows NDK LLVM:

```sh
python experiments/tsl9-resident-timer-service/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-timer-service/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

Trial names must be fresh. With retained artifacts,use `--replay experiments/tsl9-resident-timer-service/build/native-v1` for the first command and omit `--link-trial` for the second. Original register/private execution context is required. No target,HOST model or ISA execution,hardware access or vendor API traffic was performed.
