# v4.1.60 接收 guard 至佇列 provider 呼叫點

2026-11-25；原廠 BIN：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 結論

對 `0x16acc..0x16afa` 執行原指令，再銜接 `0x12bc8` 的原指令至未知 provider 入口，確認這條接收路徑傳入的**完整 A2 只有 1–8**，A0 ID 為 0–2047，來源指標為接收 frame 的 `sp+21`。payload 最多讀到 `sp+28`，恰為合成 13-byte frame 的最後一 byte。

因此，[前一批佇列單函式測試](v4160-queue-call-contract.zh-TW.md) 的長度 256、257 等案例，只是 `0x12bc8` 的任意輸入邊界，並非這條接收路徑可產生的參數。低 byte metadata 與完整 A2 的寬度差異仍成立，但在這條路徑的 1–8 範圍內兩者數值相同。

ID 零仍可通過 guard；若有空槽，會到 provider 呼叫點且 ID 欄仍為零。這不證明產生有效消費項目，provider 的行為仍未知。全佇列非零時則直接返回 `0x16afe`，不呼叫 provider。

## 逐指令證據

以下位址由本機 radare2 以 RV32 離線解碼，檢查腳本則自行解碼原始 instruction bits：

| 位址 | 指令／作用 | 結果 |
|---|---|---|
| `0x16acc..0x16ad4` | `lbu a5,17(sp)`、AND 24、非零拒絕 | `byte1 & 0x18 == 0` 才繼續 |
| `0x16ad6..0x16adc` | `lbu a2,20(sp)`、`andi a2,a2,15` | A2 的完整值先被限制至 0–15 |
| `0x16ade..0x16ae6` | `(a2-1)&255`，若無號值大於 7 則拒絕 | 僅接受 1–8；零與 9–15 被拒絕 |
| `0x16aea..0x16af8` | byte0 左移 3，OR byte1 右移 5；A1=`sp+21`；A3=S1 | ID 0–2047，payload 指標與 tag 來源確定 |
| `0x16afa` | `jal ra,0x12bc8` | queue 的返回點為 `0x16afe` |
| `0x12bf6..0x12c0c` | 寫 ID/length、載入 `[0x4004c]`、間接呼叫 | 呼叫點 A0=槽位+3、A1=原 frame+21、A2=1–8 |

## 重現

```powershell
python analysis/test_v4160_ingress_queue_chain.py
python -O analysis/test_v4160_ingress_queue_chain.py
```

僅需 Python 標準庫、原 BIN 與已發布的同目錄 `test_v4160_zero_id_queue_cpu.py`。腳本以自身位置定位 BIN，可從其他工作目錄執行。

驗證輸出：

```text
PASS: 65536 flag/length pairs (8192 accepted); 65536 headers (2048 IDs x 8); 16384 ingress-to-provider cases; 8 full queues; branch mutation detected
```

- 65,536 組 byte1/byte4 原指令檢查，8,192 組通過；對每組通過者檢查全部 A0–A3、返回位址，且 guard 不寫記憶體。
- 65,536 組 byte0/byte1 原指令檢查，確認每個 ID 恰有 8 種通過旗標的標頭編碼。
- 全部 2,048 個 ID × 8 個長度串接至 provider 入口；首空槽按 ID 模 32 分配，涵蓋全部 32 個槽位。逐例比對整個 queue、完整 A0/A1/A2 及合成 frame 的 payload bytes。
- 8 個長度的零 ID／滿佇列案例，確認返回 ingress 的 `0x16afe`，queue 不變且未執行 provider。
- 負向對照只在記憶體複本將 `0x16ae6` 的 BLTU 反轉為 BGEU，確認原本拒絕的零長度改為通過；原 BIN 不變。一般與 `-O` 模式均通過，使用明確例外檢查，沒有依賴可被最佳化移除的 `assert`。

## 證據界線與後續

這次是原指令的有限切片解譯，較先前的手寫算術投影多驗證了實際暫存器轉換、JAL 連接和 queue 寫入。合成 frame 不代表真實接收結果；尚未執行 `0x16a7c` 的取樣迴圈、provider、CSR 或任何設備。不能據此判定傳輸成功、中斷安全、所有 queue callers 都受相同限制，或可刷入使用。

本批新增驗證與分析，沒有增加 C/C++ 重建 bytes，也未重新計算整體覆蓋率。下一步可繼續查明 `[0x4004c]` 的靜態來源及已知 caller 合約，或串接接收迴圈如何寫入這 13 bytes；只採用本機可取得的證據。
