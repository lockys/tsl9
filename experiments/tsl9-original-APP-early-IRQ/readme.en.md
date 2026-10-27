# Original APP interrupt enable requests before library binding

[繁體中文](README.md) · [SDK startup/slot2](../tsl9-resident-slot2-startup/readme.en.md) · [APP callback binding](../tsl9-original-APP-library-binding/readme.en.md) · [Trap contract](../tsl9-trap-profile-contract/readme.en.md)

This study verifies existing C/C++ with **no new target code or target compilation**. Six complete functions cover328 CODE bytes/113 instructions;five vector words add20 DATA reference bytes. Original BIN,both C/C++ original-address diagnostic ELFs and two independent readers agree.

## Encoded order

Original APP initializer0x9250 calls IRQ setup0x9A42 at0x9258,before call0x9268 enters0x8E88→0x199E2. The slot2→GP+384 binding store is at0x199EC.

IRQ setup uses its own16-byte frame,setsS2=0x88 at0x9A4C and executes `csrc 0x800,s2` at0x9A50. All six RCC calls have complete existing bodies,limited to word RMW at0x40021000 offsets0x18/0x1C/0x0C/0x10 without changingS2,GP orCSR. At0x9AC2,it executes `csrs 0x800,s2` before restoring incomingS2/releasing its frame/returning. This unconditionally sets mask bits;**it does not first read and restore the incoming global mask state**.

The retained official WCH core header uses these CSR/mask operations for global interrupt disable/enable. This supports the candidate profile,not installed hardware identity. The official disable helper additionally contains `fence.i`;original0x9A42 does not. The difference is retained;no original code is changed or claimed to match the entire macro.

## Three enable requests

Each word store targets candidate PFIC IENR[1]=0xE000E104,and each corresponding priority byte is written separately:

| Store PC | Mask | Candidate IRQ /priority | Original vector target |
| --- | --- | --- | --- |
| 0x9AA0 | 0x2000 | 45,TIM3 /0x00 | 0x979E |
| 0x9AAE | 0x10 | 36,USB_LP_CAN1_RX0 /0x20 | 0x12C24 |
| 0x9ABE | 0x80 | 39,EXTI9_5 /0x30 | 0x16FB6 |

The official controller layout,IRQ enum and enable-address/mask arithmetic agree. These values **do not request BB63/LLE64 enable,and do not establish other lines are disabled**. Original BB63/LLE64 vector targets remain0x1873E/0x8498. Live enable/pending/peripheral-source states are unobserved.

Under normal returns,valid memory,callee register preservation and no asynchronous interference,the clear,six RCC calls,all priority/enable stores and final global-set dominate normal return in the complete CFG. The IRQ setup call also dominates the library-path call. **An encoded global enable request occurs before library binding;the original program cannot simply be assumed to hold every interrupt disabled until binding.**

This does not prove actual delivery,early LLE dispatch,a race or hardware failure. The asynchronous memory effects of these handlers/earlier callees remain open. Next:establish initial BB/LLE controller/source/pending states,handler effects and physical trap profile.

## Use and status

[Existing IRQ C/C++](../../src/native/irq/irq_initializer.c) · [Main C/C++](../../src/native/startup/main_family.c) · [Evidence](evidence-v1.json) · [Verification](verification-v1.json) · [Summary](summary.json)

```sh
python experiments/tsl9-original-APP-early-IRQ/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

Provide pinned local BIN,official headers and prior native artifacts;the verifier downloads nothing. Retained Windows NDK LLVM C11/C++17 artifacts are verified. Cross-platform verification is unconfirmed.

APP stays159 C/H files and95.54% byte coverage,not functional completion. SDK composition remains20,346 CODE+256 DATA with11 genuine named dependencies. The4-byte startup source gap and ROM/RAM/ISA/IRQ/stack/alias/callback/Flash/OTA compatibility remain open. No newBIN,APP integration,target/HOST-model/ISA execution or hardware access. **Usable replacement firmware has not been successfully reconstructed.** A read-only startup IRQ compatibility report remains an unimplemented future UI candidate.
