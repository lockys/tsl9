# 時鐘初始化：先讀 MMIO，再配置堆疊

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

現行 [clock_init.c](../../src/native/clock/clock_init.c) 以可讀 C 主體加最小入口／返回層，修正舊版先配置堆疊的順序差異。這是離線元件，**尚非可刷寫韌體**。

- 原廠前四條指令共12B完全相同：A5=40021000 → fresh LW A4 → A3=F8FF0000 → SP−16。
- C 主體使用入口的 A4 樣本與已配置 frame；沒有重讀該樣本、第二個 frame、spill 或 RA 儲存。只存取 SP+8／+12。
- C11／C++17 object 與 linked ELF 均240B／95指令：entry16B、C body220B、return4B。linked 無未定義符號或 relocation；object 只有兩個內部 JAL relocation。
- 85行運算 IR 經明列的 SSA／frame 對應後，等同[前版已核對的 C 核心](../tsl9-boot-clock-registers/README.md)。21次 C volatile load 加入口1次讀取，共22次；20次store。保留三個poll與原正常A2–A5條件出口。

## 驗證

需要 Python 與既有 LLVM18 工具鏈，在專案根目錄執行；不下載工具、不執行目標。

```sh
python3 experiments/tsl9-boot-clock-prefix/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --build-root "/absolute/project/experiments/tsl9-boot-clock-prefix/build/new-run"
python3 experiments/tsl9-boot-clock-prefix/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-boot-clock-prefix/build/new-run/c/verification.json"
```

實測 Windows Android NDK27.1.12297006／LLVM18；Windows 可用 py -3。每語言12項記憶體內負例直接驗證prefix、sample、jump、restore、W／poll契約，不以完整code／IR hash代替負例判定。原始BOOT與Runtime也重新讀取核對。current收據為本機build/component-v4。

## 限制與下一步

這是私有入口 ABI；不可把 body 當一般 C 函式呼叫。新增兩條 JAL x0，後續排程、PC與時序仍不同；前綴相同不代表完整IRQ／fault等價。元件VMA=0，不代表實體配置。沒有產生新BIN或進行刷寫。

下一步是將此入口接回reset／resident交接，核對實際placement、ROM身分與中斷觀察；其餘[啟動來源限制](../../analysis/boot2580-reset-resident-2026-10-22/README.md)仍保留。
