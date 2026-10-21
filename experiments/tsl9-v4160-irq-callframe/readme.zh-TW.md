# IRQ 呼叫框架 C/C++ 核心

[English](readme.en.md)

這個版本保留六次共用 RCC helper 的呼叫，取代前一版在本體內展開六次 RMW 的做法。可讀 C/C++ 表達呼叫順序、遮罩與周邊寫入；少量原生邊界原語約束 S0/S1/S2、四-byte `JAL`、CSR 與暫存器輸出。編譯器負責建立和還原堆疊框架，並非把整個原始函式貼成 assembly。

## 重現

```sh
sh experiments/tsl9-v4160-irq-callframe/verify.sh --language both
```

也可直接執行 `python experiments/tsl9-v4160-irq-callframe/verify.py --language both`。兩個 C translation unit 分別提供 main 與四個 helper，主機 C11／C++17 各通過 9184 案例、246384 斷言；每次重新核對鎖定原始 264 bytes／94 指令證據。主機測試不證明原生 inline asm、堆疊或硬體行為。

## 原生結果

C11 與 C++17 的 linked 元件皆為 main **144 bytes**、四個 helper **各 30 bytes**，均配置於原始入口；C++ 額外使用 `-fno-exceptions`，沒有額外 unwind 配置。這些大小與配置必須由實際工具雜湊及 ELF 檢查核實，不能假設其他編譯器會產生相同內容。

main 的開頭 SP 調整與 offset 10 之後的 134 bytes 與原版一致；只有四次 stack store 的順序不同。兩者都建立 16-byte frame，儲存 RA@12、S0@8、S1@4、S2@0，但新編譯器先寫 RA，原版先寫 S2。因此一般完整返回的框架可分別比較，**逐指令堆疊狀態與非同步 IRQ 等價仍未證明**。這不是對真實中斷或外部 actor 的假設。

六個四-byte JAL 的 PC、目標與 RA 連結可逐一核對；helper 的 120 bytes 完全等同原始 BIN。這解決元件原區段大小缺口，仍不能據此宣稱完整韌體、ROM、晶片、板子、啟動或 OTA 相容。任何整合映像也必須另外揭露保留的原始 raw 程式範圍與尚未通過的條件。

原生與來源證據位於 `analysis/v4160-irq-callframe-2026-10-21/`。所有原始韌體只作資料讀取；不執行或模擬 RV32，不進行 BLE／UART／CAN／實體 Flash I/O。
