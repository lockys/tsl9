# v4.1.60 TX 尾段串接本機 query／send／update 與傳輸指令

2026-11-26。原廠 APP `ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 本次去掉的合成返回

前一批 [TX 尾段驗證](v4160-tx-tail-cpu.zh-TW.md) 在 `0x16994`、`0x168de`、`0x1693e` 的入口停止並指定返回值。本次在同一組暫存器與 stack 中執行這三個本機函式體，再執行已有的 `0x16896` 原指令傳輸解譯器，直到 TX 尾段完整返回。**只有 STATUS／DATA 的讀值是合成的**，不再合成這三個函式或傳輸函式的返回值。

起點仍為未知 copy provider 返回後的 `0x16bfa`；frame、row、selector 與保存的 caller 狀態是合成 fixture。沒有證明 provider 複製成功，也沒有執行完整 TX 入口、真實外設或網路。

## 確認的直接呼叫序列

以下每列為該函式依序傳入 `0x16896` 的 A0 數值；方括號是序列，不是宣稱真實線路 bytes：

| 本機函式 | 傳輸輸入序列 | 如何處理傳輸返回值 |
|---|---|---|
| query `0x16994` | `[3, selector, 0]` | 前兩次捨棄；第三次成為 query 的返回 A0 |
| send `0x168de` | `[2, selector+1, frame[0], ..., frame[N-1]]` | 不因返回零或逾時中止 payload 迴圈 |
| update `0x1693e` | `[5, selector, 8, 8]` | 第四次 A0 留至返回，但 TX 尾段隨即覆蓋，不用它判定結果 |

每個 wrapper 的入口依 tag bits 寫 `0x40010814`，正常退出前寫 word 17 到 `0x40010810`。測試覆蓋 tag 1、2；MMIO 只記錄在合成記憶體中，沒有推定硬體用途。

穩定長度 `L=0..8`，前面有 `k=0..2` 個 selector 的查詢 bit 3 設定時，原指令共呼叫 `0x16896` **`17+L+3k` 次**，其中 send 讀取 `N=L+5` 個 frame bytes。三個 selector 都不可用則只有 9 次傳輸、返回 4。

## 逾時與成功收到零無法由返回值區分

query 的第三次傳輸若第一或第二階段逾時，A0 都為 0：

- 第一次 query 返回零，使 bit 3 清零，因此選中該 selector。
- 最後 query 返回零，使 `0 & 0x70 == 0`，因此 TX 返回 0。

合成測試把長度 8 的全部 25 次傳輸分別設定為以下三類，三者都完成相同尾段並返回 0，但資料存取紀錄不同：

| 合成狀態 | DATA halfword 寫入總數 | DATA halfword 讀取總數 |
|---|---:|---:|
| 全部第一階段逾時 | 0 | 0 |
| 全部第一階段 ready、第二階段逾時 | 25 | 0 |
| 全部成功收到零 | 25 | 25 |

這證明的是此指定輸入下的控制／返回合約：**TX 返回 0 不是傳送或 ACK 成功證據**。不表示真實外設必能按這些獨立狀態序列工作，也不證明實際發生逾時、資料遺失或任何車輛效果。

## 重現與驗證

```powershell
python analysis/test_v4160_tx_direct_chain.py
python -O analysis/test_v4160_tx_direct_chain.py
```

使用 Python 標準庫、原 BIN 與既有同目錄的有限 CPU／TX-tail／transfer-chain 及其依賴。所有路徑由腳本位置解析，可從其他工作目錄執行。沒有修改共享解譯器，只由新子類明列額外允許的本機 PC 範圍並重用原傳輸解碼。

```text
PASS: 4096 original-callee status/tag combinations; 27 length/selector cases; 75 zero/timeout substitutions; 3 all-zero paths; 3 late-ready paths; query mutation detected
```

- 4,096 組為 selector bit 3 的八種組合 × 最後 query 的 256 種 DATA 低 byte × tag 1／2；不再直接指定 query 返回值。
- 27 組為三個首可用 selector × 長度 0–8，檢查精確傳輸序列、payload byte 讀取與呼叫數公式。
- 75 組逐一將長度 8 基準的 25 個傳輸之一替成成功零、第一逾時、第二逾時；基準初／末 query 均為零，所以這些替換不改 selector 路徑。
- 另外核對全部逾時／成功零的三條路徑，以及每階段第 255 次 ready 的三種組合。

每例比對三個本機 callees 的入口／參數、每次傳輸返回 PC／完整輸入、兩階段取樣次數、DATA 寫入／讀取、wrapper MMIO 寫入順序、row／frame 保留、最終 A0 與 RA/SP/S0–S3 恢復。改變 `0x169c6` 的 dummy 輸入 0 為 1 的記憶體複本，必須被傳輸輸入檢查抓出；原 BIN 不變。一般與 `-O` 通過。

未知指令、未映射存取或執行範圍逸出即失敗。這不是完整晶片模擬，也不含中斷、硬體副作用或 provider 身分證明。本批增加原指令串接證據，沒有新增 C/C++ 重建 bytes 或重算覆蓋率；未知 provider 及完整入口的前置條件仍可繼續離線追蹤。
