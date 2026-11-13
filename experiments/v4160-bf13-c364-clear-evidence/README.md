# V4.1.60：C364 的有界靜態證據

## 範圍與重播

唯一輸入是 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，與該下載目錄的 `catalog.json` 一致。以 BIN offset + `0x8000` 為此處程式位址；這是分析映射，不是硬體實測。`[0xc364,0xc3d4)` 即 BIN `[0x4364,0x43d4)`。驗證器先對**完整 BIN**驗長度和 SHA-256，再檢查精確窗口，獨立解碼並逐條核對指令欄位、分支及直接跳轉目標。錯誤用例直接變更記憶體中的副本或預期 fixture，不寫 BIN。

在 repository root 執行，Python 3 標準庫即可；避免寫入 bytecode：

```sh
PYTHONDONTWRITEBYTECODE=1 python experiments/v4160-bf13-c364-clear-evidence/evidence.py
PYTHONDONTWRITEBYTECODE=1 python experiments/v4160-bf13-c364-clear-evidence/test_evidence.py
PYTHONDONTWRITEBYTECODE=1 python -O experiments/v4160-bf13-c364-clear-evidence/evidence.py
PYTHONDONTWRITEBYTECODE=1 python -O experiments/v4160-bf13-c364-clear-evidence/test_evidence.py
```

Windows PowerShell 可先設定 `$env:PYTHONDONTWRITEBYTECODE='1'` 再逐行執行 Python 命令。測試固定 8 組，逐一調用且無 skip；空 fixture、空/截斷/過長窗口、完整 BIN 異動/長度異動均拒絕；亦逐項變異分支位移、直接跳轉、load/store 寬度/暫存器、PCREL 與間接跳轉及 fixture。失敗使用明確 exception，不依賴 `assert`。

測試直接讀取本目錄 `evidence.py` 的 source bytes 編譯為已註冊的正常 module，不讀寫其 bytecode cache；單用 `-B` 或 `PYTHONDONTWRITEBYTECODE` 不能阻止讀取已有 cache。新增的隔離控制在臨時目錄建立真正的 timestamp `.pyc`，再將 source 改成同長度、同 timestamp 的新內容：一般 loader 必須讀出舊值，而 source loader 必須讀出新值，並確認 cache 未變。臨時 cache 隨目錄移除，不動既有 cache。此解碼器故意只接受本窗口指令子集；不是全 ISA 解碼器。

## 獨立反組譯交叉檢查

本次另以本機 radare2 6.2.4 的 RISC-V 解碼器只讀交叉檢查（不是執行目標；radare2 並非重播必要依賴）：

```sh
r2 -q -a riscv -b 32 -m 0x8000 -c 'e scr.color=false; pd 36 @ 0xc364' firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

以下表是實際窗口全部 36 條完整指令。直接 JAL/條件目標用指令所在 PC 加解碼出的有號位移；PCREL 計算按 32 位模數。其範圍擴大超過 `0xc3be`，因為 `0xc3be` 是另一段的 **4-byte 指令起點**；繼續至其間接尾跳 `0xc3d2` 結束。`c364` 本段在 `c3aa` 返回；`c3ac` 在 `c3ba` 尾跳，不順落至 `c3be`。

| PC | bytes（記憶體順序） | 指令 |
|---|---|---|
| c364 | 4111 | addi sp,sp,-16 |
| c366 | 22c4 | sw s0,8(sp) |
| c368 | 06c6 | sw ra,12(sp) |
| c36a | 97070020 | auipc a5,0x20000 |
| c36e | 83c767ba | lbu a5,-1114(a5) |
| c372 | 17040020 | auipc s0,0x20000 |
| c376 | 1304a4b8 | addi s0,s0,-1142 |
| c37a | 81c7 | beq a5,zero,0xc382 |
| c37c | 0145 | addi a0,zero,0 |
| c37e | ef20903f | jal ra,0xef76 |
| c382 | 83476401 | lbu a5,22(s0) |
| c386 | 93f7f70f | andi a5,a5,255 |
| c38a | 81c7 | beq a5,zero,0xc392 |
| c38c | 0145 | addi a0,zero,0 |
| c38e | eff01f9e | jal ra,0xbd6e |
| c392 | 83477401 | lbu a5,23(s0) |
| c396 | 93f7f70f | andi a5,a5,255 |
| c39a | 89c7 | beq a5,zero,0xc3a4 |
| c39c | 97070020 | auipc a5,0x20000 |
| c3a0 | a38b07b6 | sb zero,-1161(a5) |
| c3a4 | b240 | lw ra,12(sp) |
| c3a6 | 2244 | lw s0,8(sp) |
| c3a8 | 4101 | addi sp,sp,16 |
| c3aa | 8280 | jalr zero,0(ra) |
| c3ac | 93072003 | addi a5,zero,50 |
| c3b0 | 17070020 | auipc a4,0x20000 |
| c3b4 | 230ff7b4 | sb a5,-1186(a4) |
| c3b8 | 0545 | addi a0,zero,1 |
| c3ba | 6fd0af89 | jal zero,0x9454 |
| c3be | b7070400 | lui a5,0x40 |
| c3c2 | 03a38704 | lw t1,72(a5) |
| c3c6 | 7146 | addi a2,zero,28 |
| c3c8 | 8145 | addi a1,zero,0 |
| c3ca | 17050020 | auipc a0,0x20000 |
| c3ce | 130525b3 | addi a0,a0,-1230 |
| c3d2 | 0283 | jalr zero,0(t1) |

## 精確條件與限制

- `c36a/c36e` 讀 unsigned byte **0x2000bf10**；接著 `c372/c376` 設 `s0=0x2000befc`，再以讀得的 `a5` 判斷。非零時 `a0=0`、呼叫 `0xef76`；零時跳過。不能假設呼叫正常返回、`a0/a5` 維持、或它沒有寫記憶體等副作用。
- 到達 `c382` 時才讀 `s0+22`；若 `s0` 仍為 `0x2000befc`，這是 **0x2000bf12**。非零時 `a0=0`、呼叫 `0xbd6e`；零時跳過。`lbu` 已零擴展，後面的 `andi 255` 不改這個值。前一呼叫可能改變 `s0`、讀取位置或內容；不憑 ABI 把它當成已證明保存。
- 到達 `c392` 時才讀 **當時的** `s0+23`；若 `s0` 仍為 `0x2000befc`，這是 **0x2000bf13**。零則 `c39a` 跳到 epilogue，沒有執行本段 `c3a0` store；非零則 `c39c` 重新計算 `a5`，`c3a0` 的 **`sb zero`** 將 0 寫入固定的 `0x2000bf13`。此 store 並非寫 1、並非以 `s0` 為 base，也不依賴呼叫保存 `a5`。即使第二個呼叫改了 `s0`，讀取地址可能變，但 store 目標仍由新的 PCREL 決定。
- 因此若各次呼叫正常返回、所需被保存狀態和 stack/return address 完好、到兩個讀點的 `s0` 均為 `0x2000befc`、訪存成功且無 IRQ/其他干擾、也無影響相關讀寫的 alias/其他副作用，順序是讀 BF10 →（非零才呼叫 EF76）→ 讀 BF12 →（非零才呼叫 BD6E）→ 讀 BF13 →（非零才寫 BF13=0）→ 還原 ra/s0、ret。上面三個條件均是**各自讀取時的值**，不是 entry 時快照；取消任何前提就不能以此簡化。即使本段跳過 store，也不能聲稱呼叫或其他行為沒改 BF13。
- 靜態只能說各個呼叫被對應分支阻止或發出；呼叫可能不返回、改記憶體、破壞預期暫存器/stack 或產生其他未知副作用。讀寫可能 fault，間接變更/中斷亦未排除。`ret` 的確切目的地依載入的 ra；上述不是動態執行證據。
- 另外 `c3ac` 寫 byte 50 到 `0x2000bf0e`，`a0=1` 後直接尾跳 `0x9454`；`c3be` 從 **0x00040048** 載入一個 word 到 `t1`，設 `a2=28, a1=0, a0=0x2000befc`，再 `jalr zero,0(t1)`（目標最低位清零）。slot 形狀、實際目標、返回與副作用未知，不能稱其為 memset。

此報告只證窗口內容和所列條件，未宣稱完整函數邊界、全局呼叫者、所有可能 entry、全局寫入或沒有其他 alias。未做 raw JAL 全 BIN 掃描；即使做 raw 掃描，匹配也不等於已證指令邊界或全局呼叫圖。未證 `0x1550e → 0xc3be` entry path。無模擬、燒錄或硬體執行。
