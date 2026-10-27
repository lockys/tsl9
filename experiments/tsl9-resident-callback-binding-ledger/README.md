# Callback 條件式綁定

[English](readme.en.md) · [目前 C/C++ 本體](../tsl9-resident-scheduled-record-callback/README.md)

本輪把已重建候選 SDK 的 **51 個間接呼叫點**，與原 APP 的設定、註冊及表格來源串接。核對 **14 個完整 SDK 函式／4,730 bytes／1,629 指令**；[驗證收據](verification-v1.json) 與 [逐點清單](ledger-v1.json) 保留位址、條件及證據。

| 路徑 | 點數 | 條件式結果 |
| --- | ---: | --- |
| Raw clock | 7 | 已接受原 APP 時鐘設定、槽值穩定時，目標為 `0x191C6` |
| Clock provider | 2 | TimerInit 傳入／完成註冊的指定情境，目標為 `0x43D62` |
| Sample／calibration | 4 | 原 BLE 設定完成複製且維持穩定時，目標為 `0x197F0`／`0x197B8` |
| Status | 5 | 已知複製後的 staCB 仍為零時，走原 guard 略過呼叫 |
| Scheduled record | 1 | 指定 producer／table／event 條件下，`0x43390` 呼叫 `0x56CDC` |
| 本輪未串接 | 32 | 不推算為缺失函式；保留先前其他條件式分析 |

`0x43538` 呼叫 provider，provider 再於 `0x43D7A` 呼叫 raw clock，兩層不可混用。TimerInit 的校準呼叫 `0x43F60` **早於**時鐘設定驗證，不能以「時鐘設定已成功」作為其必要前提。

Status 的結論只限於已知複製後零值情境；先前 heap 呼叫時的值仍未證明。`0x59E20` 是由第一個 `0x59E0C` guard 的零值分支略過，原程式沒有第二個 null guard。排程證據僅涵蓋 event bits 0..14；ID31／47 不在這項證明內，不代表一定不能使用。

已重新讀取原 byte、完整 CFG、指標傳遞、現有 C11／C++17 物件與獨立 ELF 讀取器，並重查原 APP callback 設定證據。舊遞迴驗證鏈的收據以雜湊固定，本輪未重新執行整條舊鏈。所有綁定仍需要原 private ABI、有效不重疊的記憶體、正常返回及無非同步覆寫等條件；未觀察 live 綁定。

沒有新增目標 C/C++、編譯或 BIN。現有候選組合維持 **35,324 CODE + 256 DATA bytes／12,195 指令／0 具名 UND**；APP 靜態覆蓋率仍為 **95.54%**，不是功能完成率。原機 ROM／RAM／ISA／IRQ／Flash／OTA 相容性、全域初始化順序及既有 4-byte 啟動來源缺口仍未解決，**尚不可宣稱可燒錄**。

可考慮加入只讀 callback 路由診斷；本輪未實作硬體控制或改寫原行為。

離線重跑（在專案根目錄，`LLVM_BIN` 指向既有 LLVM 工具目錄）：

```sh
python experiments/tsl9-resident-callback-binding-ledger/verify-v1.py --tool-dir "$LLVM_BIN"
```

輸出結果不執行 target、HOST model、ISA 模擬、硬體或網路操作。
