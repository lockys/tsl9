# v4.1.60：setter 實參、零值尾跳與另一處 flag writer

承接 [hook 登錄與 fresh flag 保存條件](v4160-hook-lifetime-static.zh-TW.md)，本輪把已核對的 setter 接到八處具體常數實參、兩處零值尾跳，以及另一個條件性 flag writer。兩份 resident 都只作**候選映像**，未認定實際 installed provider。

新增範圍是 14 個有界視窗、316 bytes／114 指令，並非 14 個完整函式。只做原 bytes、operands、條件 CFG、地址及 bit 判定算術；沒有執行或模擬目標 ISA、callback、RAM、stack、CSR、ECALL 或硬體。既有 C 重建 bytes 未增加。

## 四組常數實參：callee 與傳入 callback 是不同地址

下表每個視窗完整包含連續三條標準指令：`LUI A0`、`ADDI A0,A0`、`JAL RA,setter`。中間沒有其他指令重定義 A0 或插入 call。每份各四個視窗，合計 96 bytes／24 指令。

| V1.31 FLASH 視窗，end-exclusive | V1.40 FLASH 視窗，end-exclusive | V1.31 A0 | V1.40 A0 |
|---|---|---|---|
| `0x416b8..0x416c4` | `0x416f8..0x41704` | `0x20000d50` | `0x20000d50` |
| `0x4202a..0x42036` | `0x4206a..0x42076` | `0x5c9b4` | `0x5cafc` |
| `0x4249e..0x424aa` | `0x4252a..0x42536` | `0x62924` | `0x62a0e` |
| `0x424c8..0x424d4` | `0x42554..0x42560` | `0x62924` | `0x62a0e` |

LUI／ADDI 的組合分別為 `0x20001000-688`、`0x5d000-1612/-1284`、`0x63000-1756/-1522`。FLASH 座標的 JAL target 是 `0x409fa`／`0x40a3a`；經各自 first-copy 映射後，真正的 RAM 座標 target 均為 setter `0x2000078a`。不能將 A0 的值誤報成該條 JAL 的呼叫目標。

RAM 參數 `0x20000d50` 對應 first-copy 來源 `0x40fc0`／`0x41000`。本輪只驗證這個地址的映射，不宣稱已驗證它的 callback 本體。其餘參數是兩份候選中不同的 FLASH 地址。

若這些視窗實際被到達、setter 與資料映射符合候選且存取有效，原 setter 會把這些非零 raw pointer 存入各自 hook slot，接著設 flag=1。這是登錄，不是執行 callback；沒有建立不同登錄路徑的先後順序或首次執行時點。

## 傳入零的尾跳：清 slot 仍不等於清 flag

V1.31 `0x60734..0x60740`、V1.40 `0x6081e..0x6082a`，各 12 bytes／4 指令：

```text
LI A0,0
SP+=32
AUIPC T1,0x1ffa0000
JALR X0,T1,82 / -152
```

以 AUIPC 自身的 FLASH PC 算上 signed immediate 再清 bit0，兩者 target 均為 `0x2000078a`。JALR 的 rd 是 X0，沒有本機 link；這是尾跳，不能當作普通 linked call。此視窗也沒有重寫 RA，尚未驗證更早 epilogue 如何恢復它。

若路徑實際到達、SP／RA／存取條件成立並進入候選 setter，A0=0 會清 hook slot 並保留原 flag。不能從這個清除路徑推出 flag=0 或 callback 資源已釋放。

## prefix 可直接進入 flag writer，無需經過未知中段

V1.31 prefix `0x42044..0x42072` 與 V1.40 `0x42084..0x420b2`，各 46 bytes／19 指令，均映射至 `0x20001dd4..0x20001e02`。

prefix 先配置 64-byte frame，將 RA／S0..S11 保存至 offsets `60,56,52,48,...,12`。它讀取 state word，做 32-bit `SLLI16`，然後 `BGE A4,X0`：

| 候選 | state word | BGE 的 FLASH PC | taken target |
|---|---|---|---|
| V1.31 | `0x2000352c` | `0x4206e` | `0x42268` |
| V1.40 | `0x2000357c` | `0x420ae` | `0x422a8` |

taken 的條件是載入值的 bit15 為零。檢查器核對所有 65,536 個 low16 值；較高的 input bits 由 32-bit shift 丟棄。這條 taken edge 直接落到下述 writer tail，中間沒有 call。13 組保存欄位與 tail 的 restore 欄位逐一相符，因此在正常存取及無干擾條件下，這條分支有具體的 frame 建立來源。

另一條 fallthrough 進入尚未驗證的中段；本輪明列這個 cut，沒有聲稱整個 enclosing function 已完成，也沒有把中段的硬體或其他副作用納入已證明範圍。

## writer tail：依 fresh pointer+108 設 flag=1

V1.31 `0x42268..0x4229c` 與 V1.40 `0x422a8..0x422dc`，各 52 bytes／22 指令，均映射至 `0x20001ff8..0x2000202c`。完整 tail 是：

```text
pointer = fresh U32[pointer_source_word]
field   = fresh U32[pointer+108]
if field != 0:
    SB1 flag
LW RA,60(SP)
LW S0..S11,56..12(SP)
SP+=64
RET
```

| 候選 | pointer_source_word | flag | tail SHA-256 |
|---|---|---|---|
| V1.31 | `0x2000353c` | `0x20002efc` | `706c380eb91490005bbac643de5c0662caeb464bc77ffd4c7cc8063fad1f8dda` |
| V1.40 | `0x2000358c` | `0x20002f4c` | `2293c2a96b42af339e31532e3300b5483ae8f9e9edf62b477a0f8e3b9b70af1a` |

第一個 pointer 沒有 local null guard，就讀其 +108 word；因此有效物件與可讀地址都是前提，不能把 null pointer 解讀為安全退出。第二個 word 為零時跳過 SB，原 flag 保留；非零時才寫 1。這裡不讀 flag、不清 flag，也不寫 hook slot。

兩個 flag 地址已與先前 setter／JT2 callback／consumer 的地址精確相接。這補上一個「並未登錄新 pointer，仍可設 flag=1」的本機來源；若此寫入實際介於 callback 清 flag 與 consumer 的 fresh read 之間且值保留，會抑制 consumer 的本機 slot 清除。是否發生該時序、pointer+108 的意義與來源都還未知，不能當作 observed execution。

## raw candidates 與可靠局部視窗分開記錄

對每份完整 carrier，以 halfword offset 掃描 JAL／C.J／C.JAL 到 source setter，得到各 5 個 raw candidates；鄰接 AUIPC／JALR 形成 RAM setter 的 pattern 各 23 個。完整 PC 清單保存在 ledger。四個常數視窗只覆蓋前者中的四個；第五個 loaded-argument caller 與大部分鄰接 pair 還需要上下文。

APP 對相同 RAM setter 的這兩類 raw pattern 均無命中。這只描述指定 encoding scan 的結果，不排除 JT／register indirect calls、分離的地址建構、其他搬移方式或未知 provider。

raw scan 可能命中 data 或 32-bit 指令中間的 halfword，不能直接當作實際 caller；例如此次複核已排除一個其他地址的 mid-instruction 偽邊。報告中的具體實參／writer 合約依據上面完整有界 operands，沒有依 raw census 推論可達性。這也不是所有 flag writers 的普查。

## 重播與尚未解除的邊界

[檢查器](check_v4160_hook_callers_flag_static.py) 與 [完整 ledger](v4160-hook-callers-flag-static.json) 的重播方式：

```text
python analysis/check_v4160_hook_callers_flag_static.py
python -O analysis/check_v4160_hook_callers_flag_static.py
```

一般與 `-O` 模式都逐 byte 重現 ledger，並驗證原 APP／兩份候選／SDK／sparse 來源身分、14 個視窗的每條 operands 與 SHA-256、FLASH／RAM branch／call 座標、13 組保存欄位、65,536 個 bit15 判定與 46 個指定原指令 mutation。指令變異必須被對應 operand 檢查拒絕。

APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本輪沒有增加 C 重建覆蓋。

接續可追查 loaded-argument caller、具體 callback 本體、pointer-source word 與 +108 欄位寫入者，以及尚未驗證的函式中段。實際 installed binding、ECALL 路由、物件／frame 保存期與其他 writers 仍保留未知。
