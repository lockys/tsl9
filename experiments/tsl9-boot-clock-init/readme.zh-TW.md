# BOOT／Runtime 時鐘初始化 C/C++

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

以普通可讀 C 重建原廠時鐘初始化；來源整理在 [src/native/clock/clock_init.c](../../src/native/clock/clock_init.c)。除了不產生指令的frame-storage port，沒有指令承載、ASM演算法或fake provider。

## 驗證結果

- C11／C++17 object與linked元件皆為 **214B／88指令**，只有一個真正FUNC及AX區段；無UND／ABS／relocation。
- 原BOOT與Runtime的234B／93指令逐byte相同，詳見[來源核對](../../analysis/boot2580-clock-2026-10-22/README.md)；新C機器碼不等於原版。
- 實物核對SP／A2–A5寫入範圍、16B frame及SP+8／12。IR保留22次load／20次store、三個poll、fresh counter／ready／postloop狀態與兩次同值寫回。原43個存取位置在候選為42個：ready的0／1分支合併為一次store，沒有省略路徑上的寫入。

## 使用方式

在專案根目錄，指定既有LLVM、兩份原BIN及全新build目錄：

```sh
python3 experiments/tsl9-boot-clock-init/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --boot-firmware "/absolute/ID-2580-V1.0.00-decoded.bin" --runtime-firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-init/build/new-run"
python3 experiments/tsl9-boot-clock-init/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-init/build/component-v1/c/verification.json"
```

Windows可用 `py -3`／`python`。本輪實測Windows Android NDK27.1.12297006／LLVM18；verifier核對完整來源／工具／標頭hash及實際編譯依賴，其他平台未實測。完整SSA／CFG hash是固定配方護欄，不是獨立ISA語意證明。

## 限制

原版先讀MMIO再減SP，候選先配置frame；出口A2–A5值、fault／IRQ／非同步與完整ABI仍未證。後兩個poll維持沒有軟體timeout，普通返回不代表硬體ready保證。

元件VMA=0只是離線連結配置，尚未納入啟動層或OTA BIN；不證明原機resident、實體頻率或可刷寫性。沒有執行目標、MMIO、HOST測試或硬體操作。
