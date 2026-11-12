# V4.1.60 `0xb0b0` 四個直接邊的局部證據

唯讀固定輸入 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76,800 bytes，映像 offset 0 對應 PC `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。`verify.py` 獨立固定全檔 hash 和以下五段完整原始 bytes；檢查不依賴 `assert`，亦獨立解碼四個 JAL 位移和 AUIPC/SB 位址。窗口均為半開區間；精確 bytes 位於 verifier 的 `WINDOWS`。

離線靜態上下文取自索引中的 r2 6.2.4：唯讀 raw 映像以 `-n -a riscv -b 32 -m 0x8000` 載入，分別在 `0x102bc`、`0x16266` 和 `0xb0b0` 起按指令反組譯。verifier 不執行 r2；除 JAL、位址運算之外，指令語意是 r2 解讀，非 verifier 全指令獨立解碼。

| 窗口 | 直接邊 | 局部條件與作用 |
|---|---|---|
| `[0x102bc,0x10300)` | `0x102e6`: JAL ra，位移 -21046 | 從窗口起點依序進入時：`lbu a5,7(a5)` 的 bit 2 必須為 1；`s0` 無號大於 137；`lbu a5,311(gp)` 為 0；`0x8202` 返回的 a0 非零，且 `0xac0a` 正常返回。然後 `a0=4` 呼叫 `0xb0b0`。返回 `0x102ea` 後重新載入 `a5=*(gp+309)`；若非零跳至 `0x10318`，否則寫 1 並呼叫 `0xd052`，將其返回 a0 與 4 比較。`0xb0b0` 返回的 a0 並非該比較的值。其他入口或例外不在此路徑條件內。 |
| `[0x16266,0x16276)` | `0x16272`: JAL x0，位移 -45506 | 從窗口起點順序進入時，從舊 sp 的 +8/+12/+4/+0 恢復 s0/ra/s1/s2，設 a0=1，sp 加 16，尾跳 `0xb0b0`。 |
| `[0x16276,0x16286)` | `0x16282`: JAL x0，位移 -45522 | 同上恢復順序與 sp 調整，a0=2。 |
| `[0x16286,0x16296)` | `0x16292`: JAL x0，位移 -45538 | 同上恢復順序與 sp 調整，a0=4。 |

三個尾跳窗口的選擇條件不在窗口內，故不推斷其上游分支；順序描述以相應窗口起點被進入、堆疊讀取有效為條件。JAL x0 不寫入新的 ra；`0xb0b0` 的 ret 使用當時 ra，不能單憑此確定動態返回情況。

`[0xb0b0,0xb0ba)` 精確 bytes：`97 17 00 20 a3 8d a7 e2 82 80`。r2 解讀為 `auipc a5,0x20001; sb a0,-453(a5); ret`。32 位位址算術：`0xb0b0 + 0x20001000 - 453 = 0x2000beeb`；SB 取 a0 低 byte。這是靜態有效位址計算，不證明該位址可寫、硬體意義或實際寫入。

不是全 caller 盤點、完整 CFG、可達性證明、執行時觀察或硬體 ABI 證明；不假定所有呼叫正常返回，也不推斷其他映像。未執行或模擬韌體、編譯、使用網路或硬體，亦不操作 settings。

從 repo 根目錄離線執行（Python 標準函式庫）：

```text
python -B experiments/v4160-b0b0-direct-edge-evidence/verify.py
python -B experiments/v4160-b0b0-direct-edge-evidence/test_verify.py
python -B -O experiments/v4160-b0b0-direct-edge-evidence/test_verify.py
```

測試直接對每個窗口的每個 byte 突變、每個窗口內的每個截斷長度檢查拒絕；另測全檔身分、JAL 實例與有號欄位邊界。窗口測試直接調用局部檢查，避免僅由全檔 hash 擋住而掩蓋窗口檢查缺陷。
