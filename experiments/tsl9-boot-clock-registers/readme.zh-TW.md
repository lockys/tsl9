# 時鐘初始化：正常出口暫存器

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本版以可讀C與空的固定暫存器port保留原版正常返回時的A2–A5。現行 [src/native/clock/clock_init.c](../../src/native/clock/clock_init.c) 已採用[入口順序修正版](../tsl9-boot-clock-prefix/README.md)；本版224B來源與驗證保留作比較。

## 本輪結果

C11／C++17 object與linked元件皆為 **224B／91指令**，一個FUNC／AX區段，無UND／ABS／relocation。保留16B frame、22次volatile load／20次store、三個poll及兩次同值寫回；沒有增加硬體讀取或timeout。

令W為最後一次fresh SP+12讀值：

| 正常RET路徑 | A2 | A3 | A4 | A5 |
| --- | --- | --- | --- | --- |
| W≠1 | 0x20000 | 0x40021000 | 完整W | 1 |
| W=1且後續poll正常結束 | 0x20000 | 0x40021000 | 8 | 8 |

W≠1不能一律當成0；只有無干擾且coherent private stack時才可如此特化。[原始來源與caller核對](../../analysis/boot2580-clock-exit-2026-10-22/README.md)確認殘值會帶至resident邊界，未證明是dead registers。verifier重播該證據，再核對實際IR兩個phi、四個GPR輸出及raw／LLVM出口指令。

## 離線驗證

```sh
python3 experiments/tsl9-boot-clock-registers/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --boot-firmware "/absolute/ID-2580-V1.0.00-decoded.bin" --runtime-firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-registers/build/new-run"
python3 experiments/tsl9-boot-clock-registers/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-registers/build/component-v2/c/verification.json"
```

實測Windows Android NDK27.1.12297006／LLVM18；可將python3換成py -3／python。其他平台未實測。工具、來源、標頭與遞迴來源證據均固定hash。component-v1是去重來源pin前的歷史快照，current replay使用v2。

這只核對條件式正常四GPR投影；首個MMIO讀取與frame順序仍不同，完整ABI／fault／IRQ／非同步／ROM及實體相容性未證。元件VMA=0，未整合啟動層或OTA BIN，沒有執行目標或硬體。
