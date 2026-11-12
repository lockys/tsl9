# V4.1.60 `0xb0b0` 尾跳的有界暫存器證據

本實驗銜接 `experiments/v4160-b0b0-tail-dispatch-evidence/`，但自行固定完整原 bytes，不依賴其程式。唯一輸入是 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 `0x12c00`（76,800）bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；raw offset 0 對應 PC `0x8000`。

`verify.py` 固定下列**完整半開窗口**的原 bytes，包含所有三條尾跳與 leaf，不只是指令子集：

| 窗口 | 長度 | 內容 |
|---|---:|---|
| `[0x155d0,0x15650)` | 128 | 入口、分支、表基址與間接跳轉 |
| `[0x16266,0x16296)` | 48 | 三組恢復、a0 賦值與尾跳 |
| `[0xb0b0,0xb0ba)` | 10 | leaf：`97 17 00 20 a3 8d a7 e2 82 80` |
| `[0x1a9f4,0x1aa00)` | 12 | 三個表 word，實際從 BIN 指定地址讀取 |

## 條件式順序路徑與暫存器

以下僅討論從 `0x155d0` **順序進入**，入口完整 `a0=A` 的低 byte 是 `c1`、`c2` 或 `c3`；`*( *(gp+84) + 4)` 的 bit 3 為 0，`*(gp+358)` byte 為 0；所有相關指標、stack 和表的讀寫成功，路徑執行期間所需指令及資料不受別名寫入或其他事件改變，也沒有例外或外部暫存器干擾。這些是前提，不是實際可達性或執行證據。

- `0x155e6` 對 bit 3=0 跳到 `0x155f6`，跳過 `0x155f0` 的 `li a4,2`。bit 3=1 時，對這三個 selector `(A+6)&255` 分別是 `c7/c8/c9`，均大於 2，故 `0x155f2` 轉到 `0x1578c`，不是本路徑。
- `0x155fa` 在 `gp+358==0` 時跳到 `0x1560e`。`0x15612` 先令 `a4=(A-1)&255`，得到 `c0/c1/c2`；`0x1561a` 因其大於 7 跳到 `0x15630`，**跳過** `0x1561e..0x1562c` 的 a3/a2/a1 賦值及對 `0x9124` 的呼叫。這點是沿路保留 a1–a3 的必要條件，而非假設被呼叫函式保留它們。三個 index 也都不大於 252，通過 `0x15638`。
- `0x1563c` 的 `auipc a4,5` 先把 a4 設為 `0x1a63c`；`0x15640` 的 `addi a4,a4,184` 再設為 **`0x1a6f4`**。之後 `0x15644..0x1564e` 取表位移並以 `jr a5` 間接跳轉，不改寫 a1–a4。
- 目標的各 16-byte 窗口依序載入 s0、ra、s1、s2，將 a0 分別設為 1、2、4，sp 加 16，然後 `jal x0` 至 `0xb0b0`。對應跳轉指令是 `0x16272: 6f 40 ff e3`、`0x16282: 6f 40 ff e2`、`0x16292: 6f 40 ff e1`。這些指令不寫 a1–a4，也不以 JAL 寫新的 ra。
- leaf 的窗口是 `auipc a5,0x20001; sb a0,-453(a5); ret`，只寫 a5、記憶體及控制流程，指令不寫 a1–a4。故在上述**條件路徑**上，a1–a3 等於 `0x155d0` 的入口值；a4 先變成 index、再變成 `0x1a63c`，在 `0x15640` 後為 `0x1a6f4`，尾跳與 leaf 窗口均不改寫它。這不表示 a4 從入口起一直不變。

## 表算術與可重播性

verifier 手寫解碼 `0x1563c` 的 AUIPC 與 `0x15640` 的 ADDI，檢查 opcode、rd、rs1、funct3 及有號立即數：`0x1563c + (5 << 12) + 184 = 0x1a6f4`。AUIPC 基準是其自身 PC。用 `(A-1)&255` 索引，表項是相對**表基址**的有號 LE32 位移；RV32 加法取低 32 位，間接跳轉清除 bit 0：

| 入口 a0 低 byte | index | 表地址 | bytes / 位移 | 目標 |
|---|---:|---:|---|---:|
| c1 | c0 | `0x1a9f4` | `72 bb ff ff` / `-0x448e` | `0x16266` |
| c2 | c1 | `0x1a9f8` | `82 bb ff ff` / `-0x447e` | `0x16276` |
| c3 | c2 | `0x1a9fc` | `92 bb ff ff` / `-0x446e` | `0x16286` |

指令語意來源是 r2 6.2.4 的唯讀反組譯**加人工審查**，不是 verifier 對全部 opcode 的自動解碼或完整 CFG 證明；verifier 只獨立解碼 AUIPC/ADDI 與表 word，其餘依固定窗口和人工解讀。從 repo 根目錄可重播靜態反組譯：

```text
C:\Users\locky\Tools\radare2\bin\r2.exe -n -a riscv -b 32 -m 0x8000 -q -c "e scr.color=0; pd 46 @ 0x155d0; px 12 @ 0x1a9f4; pd 21 @ 0x16266; pd 3 @ 0xb0b0" firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

```text
python -B experiments/v4160-b0b0-tail-register-evidence/verify.py
python -B experiments/v4160-b0b0-tail-register-evidence/test_verify.py
python -B -O experiments/v4160-b0b0-tail-register-evidence/test_verify.py
```

測試直接繞開全檔 hash 測每個窗口**每 byte 的每 bit**、窗口內逐長度截斷與地址偏移；另以 mock SHA 驗證 `verify` 確實到達每個 window guard。獨立突變 AUIPC/ADDI 的每個欄位位元、表 word 的每個位元、指令地址，測試解碼及表算術負例。一般和 `-O` 模式均使用明確例外檢查，不依賴 `assert`。

此證據不聲稱入口實際可達、leaf 的 `ret` 成功返回、a4 之後如何使用、完整 caller ABI 或所有其他路徑；也不證明硬體 store 成功。未編譯或執行 C/ELF、target 或模擬，未使用網路。
