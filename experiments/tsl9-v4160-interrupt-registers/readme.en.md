# Interrupt initialization with normal register contracts

This C/C++ component reconstructs ID2966 V4.1.60 `0x9A42..0x9AD2` and four 30-byte RCC helpers at `0x19124`, `0x19142`, `0x19160`, `0x1917E`. The initializer occupies 144 original bytes; the five functions total 264 bytes / 94 instructions. The earlier 118-byte initializer and 22-byte helpers preserve memory effects but overwrite A2/A3, unlike the original. Those smaller bodies cannot be counted as available original-layout space.

Each helper reads a fresh 32-bit MMIO word and returns the updated word in A0. A1 retains the exact incoming enabled bits, including noncanonical nonzero values. On the enabled path A4 is `0x40021000` and A5 is the fresh word; on the disabled path those roles reverse. The initializer retains the 20 ordered MMIO/CSR effects and its normal boundary A1=0, A4=128, A5=`0xE000E000`, A0=the sixth RCC word with mask `0x101D` cleared. General native allocation is restricted to A0/A4/A5, with A1 available only for explicit commitments; encoded native destinations must separately establish A2/A3 preservation.

The hosted adapter records helper/initializer boundary outputs alongside memory/CSR events. It does not emulate a processor or prove physical register preservation. Each C11/C++17 host suite checks 4 groups / 9,184 cases / 246,384 assertions, including enabled flags with high bits, all bit-pair bases, fresh repeated MMIO reads and six distinct initializer samples.

```sh
sh experiments/tsl9-v4160-interrupt-registers/verify.sh --language both
```

Python 3.10+ and a C11/C++17 compiler are required. `CC`/`CXX` specify a single compiler executable; `PYTHON` selects the shell entry's Python. Direct Python invocation is also supported. Full mode checks the unchanged sealed original 94-instruction proof; `--tests-only` explicitly omits that source proof. New UUID build directories are ignored. Windows results do not establish Linux/macOS or POSIX-shell launch success.

Native LLVM compilation and actual object/disassembly proof are separate; see `analysis/v4160-placement-2026-10-21/compiler-review/`. Boundary preservation does not establish intermediate IRQ state, original stack/call-PC behavior, installed ROM, board, Flash or BLE compatibility. No original image is replaced, no RV32 code is executed or emulated and no firmware BIN is produced. Historical behavioral models and sealed evidence retain their original bytes.
