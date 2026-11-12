# V4.1.60 TX 第二 gate：局部靜態證據

只讀取 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，明確檢查長度為 76,800 bytes，完整 SHA-256 固定為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；flat BIN 的 file offset = PC − `0x8000`。這是身份固定，不是原廠簽章認證。精確視窗為 `[0x8a82,0x8ac0)`，包含 `0x8abe` 的完整半字：

```text
b7 07 04 00 83 a7 c7 13 93 85 01 08 82 97 85 47
63 0d f5 02 83 d7 a1 09 63 92 27 03 c1 67 f9 17
63 0e f9 00 b7 07 04 00 83 a7 c7 13 93 85 01 08
4a 85 82 97 85 47 05 46 63 0a f5 00 f2 40
```

## 獨立欄位檢查與固定的壓縮指令

`check.py` 對每條 32-bit 指令直接提取 opcode、目的/來源暫存器、funct3、立即數或 B 型位移，與人工記錄比較；對每條 16-bit 指令固定完整半字，不聲稱實作了通用壓縮指令解碼器。以下壓縮語義係人工依 RISC-V C 編碼解讀，並可與既有 `experiments/tsl9-tx-prefix-inline/prefix.c` listing 交叉參考；listing 不是本腳本的輸入。表中 bytes 為小端順序，位移相對該指令 PC。

| PC | bytes | 靜態指令及效果 |
|---|---|---|
| 8a82 | b7070400 | `lui a5,0x40` → a5=0x40000 |
| 8a86 | 83a7c713 | `lw a5,316(a5)` → 讀 word [0x4013c] |
| 8a8a | 93850108 | `addi a1,gp,128` |
| 8a8e | 8297 | `c.jalr a5`，link ra=0x8a90；目標為 a5 清除 bit 0 |
| 8a90 | 8547 | `c.li a5,1` |
| 8a92 | 630df502 | `beq a0,a5,+58` → 0x8acc；不等落到 0x8a96 |
| 8a96 | 83d7a109 | `lhu a5,154(gp)`：以當時 live gp 讀兩 bytes |
| 8a9a | 63922703 | `bne a5,s2,+36` → 0x8abe；比較當時 live s2 |
| 8a9e | c167 | `c.lui a5,16` → 0x10000 |
| 8aa0 | f917 | `c.addi a5,-2` → 0xfffe |
| 8aa2 | 630ef900 | `beq s2,a5,+28` → 0x8abe |
| 8aa6 | b7070400 | `lui a5,0x40` |
| 8aaa | 83a7c713 | `lw a5,316(a5)` → 再讀 word [0x4013c] |
| 8aae | 93850108 | `addi a1,gp,128`，使用此時 live gp |
| 8ab2 | 4a85 | `c.mv a0,s2`，使用此時 live s2 |
| 8ab4 | 8297 | `c.jalr a5`，link ra=0x8ab6；目標為 a5 清除 bit 0 |
| 8ab6 | 8547 | `c.li a5,1` |
| 8ab8 | 0546 | `c.li a2,1` |
| 8aba | 630af500 | `beq a0,a5,+20` → 0x8ace；否則 0x8abe |
| 8abe | f240 | `c.lwsp ra,28(sp)`；此處只固定第一條返回路徑指令 |

在第一次呼叫**確實返回**且 a0 != 1 的 fallthrough 上，經 8a96 比較相等及 8aa2 不相等後，第二呼叫的 a0 為當時 s2、a1 為當時 gp+128。8a96 是以 gp 為基址的記憶體讀取，s2 是暫存器比較運算元，**不是** s2 基址記憶體讀取。8a90 至 8ab4 逐條如上：本地指令沒有寫入或重載 a2、a3；不代表第一次 callee 保留它們。第二次**若返回到 8ab6 並順序執行**，8ab8 設 a2=1，先於 8aba 分支，因此不依第二次返回值而改變；不代表一定返回或到達。

兩次 load 指向相同地址，不保證讀值、callee 目標或 slot 在兩次之間穩定。這些欄位與條件路徑不證明任一 callee 會返回、遵守暫存器保存慣例、記憶體內容、外部控制流或路徑可達。也不證明 0x8acc/0x8ace 之後的行為。沒有模型驗證、目標指令執行、模擬、C target、網路或硬體操作。

## 重現

```sh
python experiments/v4160-tx-second-gate-evidence/check.py
python -O experiments/v4160-tx-second-gate-evidence/check.py
```

每次檢查完整 SHA、62 bytes、20 條連續指令及 108 個直接欄位 bit 翻轉負例。負例直接作用於已讀取的單條指令欄位並繞過全視窗 pin；B 立即數四段各翻轉一個 bit。正負例共用欄位解碼器，因此負例只測欄位敏感性，不是解碼正確性的獨立 oracle。壓縮指令負例只測精確半字固定，不測其語義解碼。檢查使用明確例外而非 `assert`，`-O` 不會移除。負例並不涵蓋所有可能變異，也不是動態驗證。
