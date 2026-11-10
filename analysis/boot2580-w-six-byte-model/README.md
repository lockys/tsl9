# ID2580 BOOT W 六 byte：條件式分片模型

## 證據與邊界

僅分析 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin`，12,288 bytes，SHA-256 `650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb`，base `0x1000` 是分析座標。沿用 [wrapper](../boot2580-w-wrapper-offline/README.md)、[前段](../boot2580-w-event-continuation/README.md)、[後段](../boot2580-w-event-return-offline/README.md) 的完整原始影像和指令 window hash 與限制。以下事件 mask `1` / `2` 不代表實際已排程；更高優先路徑、task 比對和各間接呼叫均須成立。假設 GP 與記憶體如前述分析、provider 正常返回、無未知副作用；不是硬體觀測、目標 ISA 執行或模擬器。REA 工具未提供；使用既有 LLVM 靜態解碼。

wrapper 成功進入後設 `0x200090aa..af = 55 7f 57 00 00 57`，`lhu(0x200090a6)=6`，`lhu(0x200090a8)=0`，並呼叫 `[0x40050]`，參數 mask 1。這是 buffer 而非已觀察到的線上封包。

## 精確計算及指令錨點

| PC，原始 bytes | 條件式作用 |
|---|---|
| `14e0 17890020 035969bc`, `14e8 97890020 83d909bc` | 依序讀 length 和 offset 的 16-bit 快照，在 `[0x4013c]` 呼叫前完成 |
| `14f2 8547 6319f504` | provider 完整返回值必須等於 1；否則 `1546` 清 length |
| `14f8 33093941 4209 13590901 93190901 93d90941` | 相減取低 16 bit 再 sign extend；signed <=0 時也清 length，不清 offset |
| `150e..151a` | `[0x400b8]` 返回值減 3，取低 16 bit，稱 C |
| `151c 63c2a902`, `1520 239ba106`, `1540 239b2107` | signed 差值正時 chunk=`min(diff,C)`，存 `gp+0x76` halfword；C 是 0..65535，不是飽和減法 |
| `1524 a947 17870020 230ff7b6` | byte `0x200090a4=10`；呼叫 `[0x40050]` mask 2 |
| `158c..15a0` | allocation 非零時請求 `[0x4004c]` copy，來源為 `0x200090aa + 當下 lhu(offset)`，長度為當下 `lhu(gp+0x76)` |
| `15f6..1610` | 僅在配置返回值 bit0=1 且 `[0x400d4]` 返回完整 0 時，將**當下** offset + **當下** chunk 的低 16 bit 寫回，再呼叫 `[0x40050]` mask 1 |

例如無競爭、provider 正常且每次回傳相同 `C=4`（`[0x400b8]` 回傳 7）：mask 1 準備 4；mask 2 請求 `55 7f 57 00`，成功分支 offset 0→4；下一輪準備 2，請求 `00 57`，offset 4→6；下一 mask 1 的差為 0，清 length。這是兩次 copy **請求**，不是實際 copy 或發送的證明。C≥6 可一次請求六 byte；C=1 則六次；C=0 可不前進反覆循環。返回值 2 時 C 為 65535（16-bit wrap），並非 0；空間安全、provider 語義及合理 MTU 未確立。

mask 2 開始時計數為 0 才清 length；allocation 零，或配置 bit0=0，或 submit 非零時，計數減一、請求延時事件，offset 不在該分支更新。十次失敗後計數為零，**下一次** mask 2 才清 length。submit 分支的 cfg 使用 bit0，而前一階段必須完整等於 1。沒有檢查 copy 返回值；provider 可能有未建模副作用。成功分支也未證實發送、收到、ACK、持久化或 ownership。完整參數、錯誤路徑及 SDK 僅條件比對見後段文檔。

## 重試和競爭

每次 retry 重新讀 offset、chunk 和 buffer，並非快照重放；mask 1 的 length/offset 快照又先於 provider 呼叫。競爭者可能改寫 buffer、offset、length、chunk、計數，或在 copy 和 offset 更新之間插入寫入；因此不可從模型推斷跨 retry 的一致性或原子性。例：已準備 chunk=4、第一次失敗後另一 writer 將 buffer 改為 `ABCDEF`、offset=1，下一次的 copy 請求為 `BCDE`，成功後 offset=5；這是人造交錯反例，並非聲稱真機確有此 writer。新 wrapper 把 buffer 和 offset 重設後，舊的已準備 chunk 仍可能用於新 buffer；現有證據未建立調度順序、鎖或生命周期。provider 可在指令間改狀態，實際結果不止模型所列。

## 重現與負測

依賴 closure：此目錄的 `check.py` 使用 Python 標準函式庫及下列已追蹤 gate：`boot2580-w-wrapper-offline/check.py`、`boot2580-w-event-continuation/check.py`、`boot2580-w-event-return-offline/check.py`。三者讀取本倉庫已追蹤的上述 ID2580 影像；最後一個 gate 另硬編碼讀取 **未追蹤的本機資料** `analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h`（SHA-256 `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c`）。乾淨 checkout 須自行提供完全相同的 header，否則完整 checker 會失敗；本分支不納入 SDK。此 header 僅供既有 gate 的條件式 SDK 比對，非模型或硬體執行的證明。

`python -B analysis/boot2580-w-six-byte-model/check.py` 先執行三個既有整檔與指令 window gate（含逐 byte 突變、截斷和 wrapper 負測），再執行人工導出的離散模型：4+2 完整拼接、長度結束、C=0/1/6/65535、cfg 完整值和 bit0 的差異、signed 差值負例、配置或 allocation/submit 失敗的十次重試、人工跨重試及跨 wrapper 交錯。模型以 Python slice 近似可讀記憶體，並把一次 attempt 視為原子；它不驗證越界、provider 行為或中途交錯，也不是獨立的指令語意證明。未連接設備、未刷寫。
