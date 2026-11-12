# V4.1.60 TX guard：正常 fallthrough 的局部前提

獨立離線檢查 `validator.py` 讀取兩個完整 76800-byte BIN，offset 0 對應 `0x8000`，固定整檔 SHA-256（身分 pin，非來源認證）：

* 參考 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。
* 集成候選 `artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin`：`28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`。

原始小端實體 bytes，兩者 `[0x8a6a,0x8a76)` 均為 `03d761092a893684b284ae89`：`0x8a6a` 的 `03d76109` 解碼為 `lhu a4,150(gp)`；其後四條壓縮 move 只複製其他暫存器，未改寫 a4 或 a0。若從此處連續正常執行，a4 是載入的 16-bit 值零擴展；這不能約束繞過載入的其他入口。

| PC | 參考 bytes | 候選 bytes | 精確意義 |
|---|---|---|---|
| 0x8a76 | 6310a702 | 6310a702 | **先** `bne a4,a0,+32`；不等跳 0x8a96，相等 fallthrough 0x8a7a |
| 0x8a7a | c167 | c167 | `c.lui a5,16` → 0x10000 |
| 0x8a7c | f917 | f917 | `c.addi a5,-2` → 0x0000fffe |
| 0x8a7e | 630cf700 | 638ca700 | 分別 `beq a4,a5,+24` / `beq a5,a0,+24`；目標 0x8a96，否則 0x8a82 |

B-immediate 計算為 sign-extend 13 位的 `inst[31]<<12 | inst[7]<<11 | inst[30:25]<<5 | inst[11:8]<<1`，相對 branch PC 而非後繼 PC。程式獨立解碼 opcode、funct3、rs1、rs2、位移及目標，也解碼 LHU 和壓縮常數指令，並固定上述所有 bytes。

## 全 32 位代數及邊界

令 `x=a4`、`y=a0` 為任意 32-bit 位向量。RV32 `bne` 在 `x != y` 時跳轉，因此正常 fallthrough 的條件是 `not (x != y)`，即 **x = y**。等號的替換律對任意 32-bit `z=a5` 給出 `(x=z) iff (z=y)`；這是全 32 位代數證明，**不是測試窮舉**。中間兩條指令只改 a5，所以無例外、非同步改寫或中途入口時，兩個 BEQ 的判斷一致；順序執行它們還固定 z=0xfffe。兩個比較各自目標與 fallthrough 也相同。測試僅為有限回歸例，不構成證明。

非 fallthrough 不可依賴此等式。例如直接進入 `0x8a7a`，令 a4=0xfffe、a0=0；兩條壓縮指令把 a5 設為 0xfffe，參考 BEQ 成立而候選不成立。這是**假設性內部入口反例**，不聲稱入口實際可達。`check_domain` 僅檢查給定值與聲稱的 fallthrough 前提，不能證明歷史控制流。

已有全映像參考 raw 直接候選掃描 [`scripts/scan-tx-direct-targets.py`](../../scripts/scan-tx-direct-targets.py) 在每個半字位置檢查指定 RV32/RVC 直接編碼及緊鄰 AUIPC/JALR 配對；它只固定參考映像，掃描包含資料及重疊指令，排除 TX 內部來源，間接目標未解析，配對亦只在順序執行時有效。它不是指令邊界、可達性或完整 CFG 證明，也不能排除計算跳轉、其他映射、runtime 修改、例外及非同步干擾；本實驗未重新執行該掃描。另有兩映像的[允許區掃描](../tsl9-tx-guard-compare/README.md)，但它排除部分區域與 TX 自身，同樣不是完整 CFG。

## 重播

```text
python -B experiments/v4160-tx-guard-prefix-domain/validator.py
python -B -m unittest discover -s experiments/v4160-tx-guard-prefix-domain -v
python -B -O -m unittest discover -s experiments/v4160-tx-guard-prefix-domain -v
```

負例直接送欄位 validator，包含 branch opcode、funct3、rs1、rs2、各立即數欄位突變；亦測無效 32-bit 值、非 fallthrough、不同寄存器值、窗口及完整映像突變。無 `assert` 安全依賴。只做靜態 bytes 與數學檢查；不編譯或執行 C、target 或模擬器，不接網路／硬體，不改設定；不證明整體 TX 等價、ABI、硬體或可燒錄性。
