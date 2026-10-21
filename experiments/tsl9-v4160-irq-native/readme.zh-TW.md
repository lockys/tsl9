# IRQ 原生 C/C++ 核心

[English](readme.en.md)

本元件以分支各自持有的讀取、RMW、儲存與返回路徑，取代舊核心共用的 OR／AND／選擇值。原生 I/O 邊界將基底、遮罩與正常返回值放在原本使用的暫存器，實際 RMW 與周邊存取仍由可讀 C/C++ 表達。原生編譯使用四個可配置暫存器 A0/A1/A4/A5，並停用 LLVM machine outliner；其他整數暫存器均保留。這是編譯器與原機契約之間的實作橋接，並非完整原始碼還原。

## 重現驗證

```sh
sh experiments/tsl9-v4160-irq-native/verify.sh --language both
```

也可直接執行 `python experiments/tsl9-v4160-irq-native/verify.py --language both`。C11 與 C++17 分別使用已鎖定的既有測試：每種語言 4 組、9184 案例、246384 斷言，並重新檢查原始 264 bytes／94 指令證據。測試只執行自行編譯的主機測試程式。

原生靜態檢查入口位於 [compiler-review](../../analysis/v4160-irq-native-2026-10-21/compiler-review/)。需自行提供 LLVM 工具目錄，實際工具雜湊寫入收據。它只編譯、連結、讀取 ELF 與反組譯，不執行或模擬 RV32。

## 證據與限制

四個 RCC helper（0x19124、0x19142、0x19160、0x1917E）各產生 30 bytes，與鎖定 V4.1.60 原始 BIN 的對應機器碼完全一致。這項證據適用於這些確切函式與編譯條件，不能延伸為完整映像相容性。

IRQ 初始化函式產生 180 bytes，比原始 `[0x9A42,0x9AD2)` 的 144 bytes 多 36 bytes，因此仍不能直接取代原區段。正常返回 A0/A1/A4/A5 與 A2/A3 保留可分別檢查；執行途中 A1 被用於周邊位址，堆疊、呼叫與 CSR 時序也與原程式不同，非同步 IRQ 等價仍未證明。

C++ 額外的已配置唯讀 unwind metadata 必須另行核算；函式機器碼一致不會免除其空間與整合義務。硬體料號、原機 ROM、完整配置、啟動與 OTA 相容性均未因此通過。**本元件沒有可燒錄 BIN，也不進行 BLE／UART／CAN／Flash 操作。**
