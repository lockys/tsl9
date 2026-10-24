# RF completion and retry

[繁體中文](README.md)

Original173EE–17476 covers136B,45 instructions andseven architectural regions. Actual C11/C++17 objects preserve126 non-control bytes andthree typed references;data-only original-VA encoding matches all136B. Stop-before-clear order,the16B frame/optional callback tail,callback-pointer clearing order andframeless decrement/mask/reschedule path are retained.

```sh
python3 experiments/tsl9-rf-completion/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rf-completion/build/trial-v1
```

Compilation andnormal static checks only. Thebyte counter can wrap from0 to255;this original behavior isretained,not aclaim ofbounded retries onhardware. Callback/resident ABI,original placement,memory,hardware/IRQ/OTA remain unproved. No target/HOST-model/ISA execution orBIN generation.
