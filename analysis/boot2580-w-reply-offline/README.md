# ID2580 BOOT W 成功回覆：離線指令錨點

**結論只適用另一 BOOT 版本候選**：保存的 ID2580 V1.0.00 decoded image，12,288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`。分析 base `0x1000` 是檔案座標，不是實測地址。未確認原機安裝此版，也沒有 BLE 觀測；不應依此放寬燒錄安全策略。

在 W 前置條件通過、四次寫入呼叫正常返回、1024-byte readback 全部相等且控制流未受干擾的條件下，**傳至回覆介面的資料指標為 0、資料長度為 0**。因此該介面的資料區沒有頁索引或 nonce；命令參數是 `0x57`（W）。這是靜態的回覆請求，不是成功送達或實體 Flash 持久化證據。此結論不涵蓋下游 `0x1848` 的封裝、其他隱含狀態或 BLE 線上封包；不能斷言完整線上封包一定不含其他欄位。

## 可重現指令鏈

每個 PC 的檔案 offset 為 PC 減 `0x1000`。以下 mnemonic 來自既有保存的 radare2 listing：[`retained-source.json`](../boot2580-command-adapter-2026-10-21/source/retained-source.json)，非本測試重新解碼。

| PC | 原始 bytes | 指令／意義 |
|---|---|---|
| 2282 / 2288 | `9042` / `9442` | 各讀一個 destination／live source word |
| 228a | `e31cd6f4` | 不相等跳 `21e2` 靜默返回 |
| 2290 | `e397e7fe` | 逐 word 比較迴圈 |
| 2294 / 2296 | `8146` / `0146` | `a3=0` 長度；`a2=0` 指標 |
| 2298 / 229c | `93057005` / `8da0` | `a1=87`；跳 `22fe`，繞過 `22fa` 的 S 命令設定 |
| 2308 / 230e | `2685` / `6f002079` | `a0=s1` context；跳 `2aa0` |
| 2aa0..2aaa | `2a88ae88b287368711c299e6` | 保存四參數；因 a2 為零，直接跳 `2aac`，不走帶資料路徑 `29ce` |
| 2aac..2ab4 | `ba863e86c68542856fe05fd9` | 恢復四參數並跳 `1848`，仍為 `(context, 0x57, 0, 0)` |

前提與寫入讀回的完整邊界見 [`W 範圍`](../boot2580-w-range-2026-11-01/README.md) 和 [`W 擦除`](../boot2580-w-erase-2026-11-01/README.md)。`2aba` 是另外的單 byte wrapper，W 成功路徑不經過它。指令鏈是對固定 bytes 的人工解讀，正常呼叫返回及暫存器保存是條件。

## 重播與突變

```sh
python -B analysis/boot2580-w-reply-offline/check.py
```

唯讀核對全檔 hash 與三個連續原始指令區段 `[227a,229e)`、`[22fe,2312)`、`[2aa0,2aba)`。13 個獨立記憶體內 byte 突變覆蓋比較、長度、指標、命令、跳轉及 wrapper，**繞過全檔 hash** 直接要求相同 anchor gate 拒絕。這測試來源完整性，不是執行突變指令或獨立證明語意。可使用 `radare2 -n -q -a riscv -b 32 -m 0x1000 -c 'pDj 36 @ 0x227a' <image>` 等對上述各區長度 `36`、`20`、`26` 分別重解；比對原始 bytes 而非只信 mnemonic。沒有連設備、刷寫或產生封包。
