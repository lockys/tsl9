# IRQ flag consumer (offline C/C++)

[繁體中文](README.md)

Reconstructs official ID2966 V4.1.60 `0x17002..0x17040`: clear GP+360 bit0/bit1 before calling the receive path with channel 1/2. After each call, clear the then-live GP+361/+362. The second test rereads the flag instead of caching the first result.

The original has 62 bytes/21 instructions. An actual ET_REL partial link places the 8-byte entry immediately before the 54-byte readable C body. Two genuine `R_RISCV_JAL` calls remain unresolved; all other 54 bytes equal the official code. **This does not establish equality of fully resolved 62-byte code or a flashable BIN.**

Retains the original 16-byte frame, LBU before saving RA, fresh GP/RA-slot reads after calls, and A0 residue. RA/SP belong exclusively to architectural ports under the recorded fixed-register flags. This is not an ordinary C ABI function.

```sh
python3 experiments/tsl9-irq-flag-consumer/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-irq-flag-consumer/build/my-check
```

Set `LLVM_BIN` to an existing RISC-V LLVM tool directory; `my-check` must be a new directory. No downloads, RV32 execution or MMIO execution occur. The verifier reports actual receipt paths; replace `--build-root` with `--replay` to recheck a local original, and `--require-firmware-ready` must reject.

Receive entry `0x16B0A`, downstream SPI/resident implementations and provider ABI remain open, as do complete IRQ, physical hardware and OTA compatibility. Public receipts use portable paths; original receipts remain local.
