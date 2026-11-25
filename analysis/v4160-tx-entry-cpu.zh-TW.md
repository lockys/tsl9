# v4.1.60 TX 入口順序與 copy 邊界

2026-11-26。原廠 APP `ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本次離線執行入口 `0x16b7c` 至 copy 呼叫邊界或 caller 返回，接上已有[本機 fill／header](v4160-tx-header-roundtrip.zh-TW.md)；另在明示 provider 假設下接上[TX 直接函式鏈](v4160-tx-direct-chain.zh-TW.md)。沒有操作硬體或執行 provider。

## 原指令驗證的拒絕順序

| 入口條件 | 原指令行為 | 尚未進行的讀寫 |
|---|---|---|
| row `+11` byte 不是 1／2 | 返回 4，SP／保存暫存器不變 | 不讀 `[gp+84]`、配置內容、長度、ID 或 copy slot；不寫 stack |
| tag 有效，但 `[U32[gp+84]+4]` 的 bit 3 設定 | 返回 4 | 未配置 frame、未讀 row 長度或 ID、未讀 copy slot |
| tag／配置通過，row `+2` 長度為 9–255 | 配置 64-byte frame、保存 RA/S0–S3，讀長度後走 epilogue 返回 4 | 沒有 selector、fill、header 或 copy slot 存取 |
| tag／配置通過，長度為 0–8 | 建立 selector、執行本機 fill、寫 header、讀 copy slot，間接呼叫 | APP 在此之前沒有讀取 row payload；provider 效果未知 |

資料讀取順序逐例核對為：tag；若有效則 GP slot、配置 byte；若未被配置擋下則長度；若長度有效才讀 ID halfword、最後讀 `[0x4004c]`。無效 tag 案例刻意將 GP slot 指向未映射位置，仍必須正常提前返回，且 trace 中連 GP slot 本身都不能被讀取。

長度拒絕路徑的 A5=4 來自較早的 `0x16b96`，經 `0x16c52..0x16c60` 恢復 caller 後成為返回 A0。不能只看入口直接早退而漏掉這個已建立 frame 的拒絕分支。

## 成功走到 copy 呼叫點的前綴

這裡「成功」僅指控制流程到達呼叫點。精確 21 次 stores 為：

- 5 個 word 保存 RA/S0–S3 至新 SP 的 `+60/+56/+52/+48/+44`。
- selector halfword `0x4030` 寫到 `sp+12`、byte `0x50` 寫到 `sp+14`。
- 本機 `0x8520(sp+18,0,11)` 以原指令反向清零 11 bytes。
- 三個 header byte stores：`sp+20=length`、`sp+17=(ID<<5)&255`、`sp+16=(ID>>3)&255`。

之後才 fresh-load `[0x4004c]`，於 `0x16bf8` 呼叫，A0=`sp+21`、A1=`row+3`、A2=length、RA=`0x16bfa`。長度 0 也到達此點，沒有在入口變成 RX 的 1–8 限制。逐例比對讀取順序、所有 stores、copy 參數及 frame/link，原 row 必須不變。

## 條件性的整個 TX 串接

720 個額外案例先執行完整入口到 provider 入口，再明示採用「provider 正常返回、保存 SP／stack／S 暫存器、沒有任何記憶體效果」的假設，返回 A0 指定為 `0xdeadbeef`；**這不是已證明的 provider 行為**。

接著原指令執行 TX 尾段、query／send／update 及傳輸函式，只有 STATUS／DATA 讀值為合成資料。案例為 tag 1／2 × 長度 0–8 × 八種 selector 狀態 × 五種最終狀態，檢查精確呼叫／傳輸序列及最終 A0、caller RA/SP/S0–S3。

source payload fixture 是非零 `a0..a7`，但假設 provider 無記憶體效果，所以 frame payload 保持本機 fill 的零值；測試明確確認這個差別，沒有偷補 memcpy。row 與 frame 在後續串接中保持不變。這顯示如何在未知呼叫的兩側連接已知控制流程，不代表已完成真實 provider 或硬體驗證。

## 重現與測試

```powershell
python analysis/test_v4160_tx_entry_cpu.py
python -O analysis/test_v4160_tx_entry_cpu.py
```

只用 Python 標準庫、原 BIN 與已發布的 CPU／TX-direct／transfer-chain 等同目錄依賴。一般與 `-O` 均通過：

```text
PASS: 65536 tag/config pairs (256 accepted); 65536 config/length pairs (1152 accepted); 90 ID/tag/length boundaries; 720 conditional whole-TX cases; ordered reads/stores; 2 guard mutations
```

兩個 65,536 案例矩陣分別是所有 tag／配置 byte（長度固定 8），以及所有配置／長度 byte（tag 固定 1），不是三維全部交叉枚舉。90 個邊界案例覆蓋 5 個 ID × 2 個有效 tag × 9 個長度。記憶體複本負向對照改錯配置 mask 及長度上界，必須被拒絕路徑檢查抓出；原 BIN 未改。

共享有限 CPU 只新增本入口需要的 C.LUI 解碼，預設允許的 PC 範圍不變；新子類明列 TX／fill 範圍。既有 queue、header、transfer-chain 與 NV caller 檢查也重新通過。地址可存取、frame 有效、無非同步干擾仍是前提；入口沒有一般性的 row／配置指標有效性檢查。

本批沒有增加 C/C++ 重建 bytes 或重算覆蓋率。copy provider 的實際身分／保存合約／副作用仍未知，不能據條件性整段返回聲稱傳送、ACK、硬體或可刷入功能成功。
