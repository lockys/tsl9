# Candidate pseudo-random core and callback byte range

[繁體中文](README.md) · [Settings/Flash](../tsl9-original-prebinding-settings/readme.en.md) · [Callback registration](../tsl9-resident-callback-registration/readme.en.md) · [Clock providers](../tsl9-resident-clock-services/readme.en.md)

Two actually required SDK bodies add **144 CODE bytes/52 instructions**,compiled as original-register-context C11/C++17. Both objects match;seven positive FUNC regions and four direct-control relocations reproduce original bytes. No new custom instructions. These are not recovered vendor C sources or ordinary standalone C ABI functions.

| Body | Complete range | Bytes/instructions |
| --- | --- | --- |
| Primary tmos_rand candidate | 0x433A8..0x43414 | 108/37 |
| Callback byte-range candidate | 0x43E6A..0x43E8E | 36/15 |

Adjacent range/setter siblings are excluded. Official BLE_LIB_JT(1) and actual candidate table0x40038 identify0x433A8.

## Exact core effects

The core saves word0x4002420C inS1,writes zero,executesFENCE.I and restores the word before return. Physical meaning,IRQ atomicity and installed compatibility remain unproved;this is not assumed a global IRQ lock.

It prefers callback word0x20003210,then fallback0x200031E0. A nonnull pointer calls through0x433D2,then fresh-reads state0x20002EC8,adds the callback result and writes back. Both null skip this addition. Another fresh state read precedes:

```text
state = low32(state * 214013 + 2531011)
```

After the state store and hardware-word restoration,it fresh-reads state for the result. Do not cache pre-callback state or discard callback/IRQ/alias effects. Live state,initial seed,entropy,distribution,repeatability and cryptographic quality are unverified.

## Byte range is not modulo

Function0x43E6A preserves lower/upper,calls the core and executes actualMULHSU:

```text
result = low8(lower + high32(signed32(upper-lower) * unsigned32(rand_result)))
```

Independent instruction fields confirm signedA1/unsignedA0 operand order,retained by an explicit ISA port. No modulo/MULHU replacement. Mathematically,0<=lower<upper<=255 gives[lower,upper);equal bounds give low8(lower). There is no general bound guard.

Existing complete callback0x60516 calls at0x605C2/0x606A4 with lower1 and zero-extended byte record+19 as upper,storing the result byte at record+17. Upper>1 is unproved;application field meaning/time units remain unknown.

## Original APP seed callback provenance

Initializer0x199E2 loads table0x4007C at0x19A74 and stores it atSP+52 at0x19A90:configSP+16 plus srandCB offset36. This store dominates the library config call. Actual C11/C++17 assertions verify the primary callback type uint32_t(void),64-byte config and offset36,without runtime allocation or stubs.

Candidate0x4007C corresponds to primary TMOS_GetSystemClock/BLE_LIB_JT(18). Its existing complete42-byte target0x43520..0x4354A is already supplied. Matching ROM,completed config copy64 into0x200031EC,valid pointer/callee/memory and IRQ/alias conditions connect preferred word0x20003210 to that provider. **Live RAM pointers are unobserved and indirect-call effects remain open.**

## Verification and use

[C/C++](resident_range_random.c) · [Primary ABI assertions](random_abi.c) · [Evidence](evidence-v1.json) · [Receipt](audit-result-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-resident-range-random/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local APP/SDK,official headers and retained Windows NDK LLVM native artifacts. No dependencies are downloaded;cross-platform verification is unconfirmed.

Actual C/C++ nonloadable ET_REL compositions contain **20,490 CODE+256 DATA/7,025 instructions**. All input bytes/symbols/relocations are retained,original-PC CODE ownership is unique,and two independent readers agree. A real body resolves0x43E6A,lowering genuine named dependencies from11 to **10**,without stubs. One actual opaque callback site remains;UND count is not runtime closure.

APP stays159 C/H files/95.54% byte coverage,not functional completion. The4-byte startup source gap,settings writer's additional144-byte initialization gap and ROM/RAM/ISA/IRQ/Flash/OTA compatibility remain open. No APP integration,newBIN,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** Read-only callback bounds/seed provenance diagnostics remain an unimplemented future UI candidate,without hardware parameter changes.
