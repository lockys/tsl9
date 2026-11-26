# v4.1.60：另一條 ingress 的格式、length 與 frame／queue 邊界

本階段承接 [特定 RX 至快取路徑](v4160-rx-cache-ingress-static.zh-TW.md)，完整展開 `0x12c24 → 0x18d78 → 0x12bc8` 的另一個來源。這條入口沒有前一條 RX 的 1–8 guard：length 為 0–15，queue tag 明示為 0。extended 分支不寫 caller 隨後讀成 ID 的 record+0..3；兩個入口出口都是 MRET，不能套用普通 RET 或一般 C ABI 保存假設。

全程只有原 bytes、operands、完整局部 CFG／路徑 stores 與主機區間算術；未執行或模擬 target ISA、MRET、CSR、MMIO、stack／RAM、provider 或 copy。[檢查器](check_v4160_peripheral_rx_ingress_static.py) 與 [完整 ledger](v4160-peripheral-rx-ingress-static.json)。既有 C 重建 bytes／覆蓋率不變。

## 完整本體與返回類型

| 角色 | APP 半開區間 | bytes | 指令 | loads | stores | 本機終點 |
|---|---|---:|---:|---:|---:|---|
| ingress entry | `0x12c24..0x12c58` | 52 | 17 | 3 | 0 | 兩處 MRET |
| record reader | `0x18d78..0x18e1c` | 164 | 53 | 16 | 16 | 兩處普通 RET |
| 合計 | | **216** | **70** | **19** | **16** | |

逐條固定 operands、完整 bytes SHA-256、局部指令邊界、可達節點與無迴圈。reader 的格式選擇及控制位址選擇形成四條完整路徑，均列出實際 store PCs、record 直接寫入範圍與未直接寫入範圍。16 個 stores 是兩條替代路徑合計的靜態位置數，不是每次執行的 store 次數。

APP 為 76,800 bytes，base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 producer／consumer／cache chain、reset 與 SDK／candidate／sparse 證據也重新核對，不將候選檔當作實際 installed provider。

APP `0x80c8` 的原始 word 為 `24 2c 01 00`，數值 `0x12c24`；相對 reset 形成的名義 base `0x8038` 為第 36 個 word。這只固定映像內容與位置，沒有證明實際 IRQ 編號、路由、交付或硬體 context 保存。

## 入口：32-byte frame，直接把未 cap 的長度交給 producer

入口先 fresh 讀 `U32[0x4000640c]&3`。零時直接 `0x12c54 MRET`，不配置 frame、不呼叫 reader／producer。非零時令 H=入口 SP−32，依序：

```text
18d78(A0=40006400, A1=0, A2=H+12)
12bc8(A0=U16[H+12], A1=H+23, A2=U8[H+22], A3=0)
SP+=32
12c50 MRET
```

entry 本身沒有 memory stores 或 GPR 保存序列，但有 encoded RA、SP、A0–A3、A5 寫入。MRET 不等於這些 GPR 已恢復；是否存在更外層 trap context 仍需證據。reader 不回傳另設的 status，entry 也沒有以其 A0 判斷成功。

## reader：每次 MMIO read 均保留獨立性

一般入口令 T=A0、channel=A1、R=A2，D=`T+16*完整 channel`（RV32 算術）。它沒有一般性的 channel、record null 或 extent guard。只有這個 caller 明確設定 T=`0x40006400`、channel=0、R=H+12。

1. fresh `U32[D+432]&4` 寫至 R+8，依該 bit 選格式。
2. standard 路徑另讀 fresh `U32[D+432]>>21`，word store 至 R+0；直接寫 R+0..3，沒有寫 R+4..7。
3. extended 路徑另讀 fresh `U32[D+432]>>3`，word store 至 R+4；直接寫 R+4..7，沒有寫 R+0..3。
4. 再讀 fresh `U32[D+432]&2`，byte store 至 R+9。
5. fresh `U32[D+436]&15` 寫 R+10，得到 length **0–15**。
6. 另一次 fresh `U32[D+436]>>8` 的低 byte 寫 R+19；沒有將它自行命名為實體 timestamp。
7. D+440 的四次獨立 word reads，經不同 shift 形成 R+11..14；D+444 同樣四次讀取形成 R+15..18。
8. 完整 channel=0 時 fresh 讀 T+12、OR `0x20` 後寫回；非零則對 T+16 做同樣數值操作。

首次格式 bit、ID、其他 metadata、payload 與控制 readback 均不是同一份快照；不將 OR `0x20` 宣稱為已證明的實體 acknowledge 或接收成功。兩條 ID stores 的未寫入欄位可能有先前內容，不能直接稱為零或有效型別。

reader 無 frame、callee，只有 A4／A5 的 encoded 寫入，沒有直接保存 R pointer 值到 pointer field。A0／A1／A2 的值保持，也不足以證明 ownership、資料生命週期或其他逃逸別名。

## caller 對格式的固定讀法

reader 的所有直接 record stores 都落在 R+0..19，即 H+12..31，仍在 caller 配置的 32-byte frame 中。

| 格式路徑 | caller 的 `U16[R]` 來源 |
|---|---|
| standard | 在無不利別名／writer 下，來自本次 word store，域為 0..2047 |
| extended | 本次路徑未直接寫 R+0..3；halfword 來自先前內容，不能由 R+4 的新 ID 推導 |

standard 的數值見證 `0xcf200000>>21=1657`，且此 word 的 bit 2 為零；這不是實際讀到的值，也不把首次格式 read 與後次 ID read 合併。extended 路徑是否得到 ID1657 則需其他 stack 內容與保存證據。

caller 固定讀 R+10 的 length，將其完整 0–15 值交給 producer，沒有 clamp8。source=R+11=H+23，其中 H+23..30 是八個 payload bytes，H+31 是另外寫入的 R+19，所以共有九個本次直接寫入的 source bytes。

## copy 的條件性來源與目的區間

以下只在有空槽、實際 copy 符合參考、完整 source 範圍有效、必要 context／frames 保存且無不利別名／IRQ／其他 writer 等前提下，描述 `[H+23,H+23+L)` 與 `[row+3,row+3+L)`。檢查器只算區間，不執行存取、不宣稱這些長度已觀測。

| L | source 相對 H，半開 | 超出 32-byte frame | destination 相對 row，半開 | 下一列 prefix |
|---:|---|---|---|---|
| 0–8 | `[23,23+L)` | 無 | `[3,3+L)` | 無 |
| 9 | `[23,32)` | 無 | `[3,12)` | 無 |
| 10 | `[23,33)` | `[32,33)` | `[3,13)` | `[0,1)` |
| 11 | `[23,34)` | `[32,34)` | `[3,14)` | `[0,2)` |
| 12 | `[23,35)` | `[32,35)` | `[3,15)` | `[0,3)` |
| 13 | `[23,36)` | `[32,36)` | `[3,16)` | `[0,4)` |
| 14 | `[23,37)` | `[32,37)` | `[3,17)` | `[0,5)` |
| 15 | `[23,38)` | `[32,38)` | `[3,18)` | `[0,6)` |

L=9 的第九 byte 是 R+19，copy 到 row+11；producer 正常返回後又以 tag0 store 覆寫 row+11。L=10–15 也有該覆寫，另跨進下一列。這些是指定合約下的 footprint，沒有證明實際 queue 改動、fault、資料有效性或破壞。

最後 queue slot index31 起於 `0x2000c1ac`、tag 在 `0x2000c1b7`；queue 結束於 `0x2000c1b8`，也是 cache table row0 起點。L=10–15 的目的範圍會涵蓋其前 1–6 bytes，最遠結束於 `0x2000c1be`，**沒有直接到達 row18 O=`0x2000c290`**。

## 接到 ID1657 快取後仍保留的界線

若 reader／producer 的正常存取與保存前提成立，consumer 後續取得同一項目的完整 snapshot，filter 返回零、config bit 3 清除、probe 返回非零，且 mode1 與重讀 ID1657 成立，既有 row18 copy 請求可把 **length0–15、tag0** 帶到 O。這些條件不能由單一 status 或 copy 返回值推得。

在欄位繼續保持的前提下，tag0 選擇 `0x12a08` 的 untagged 路徑，不會進 `0x16b7c`；length0 也可能先被 `0xc6a8` 的非零 gate 擋下。之後 untagged copy 若使用 O+3：長度 9 包含 O+11 的 tag，長度 10–15 又包含緊鄰配置的前 1–6 bytes。這仍只是固定區間，沒有把來源越過物件界線當成實際可達或已證明無效的存取。

entry 恢復 SP 前沒有抹除 record，resident copy 也能觀察 H+23 的 source pointer。實際 provider 是否保存該位址、更外層 trap frame／IRQ context、extended 路徑的舊 ID、並行 writer 與實體 repeated-read/control 行為仍待釐清。

## 重播

```text
python analysis/check_v4160_peripheral_rx_ingress_static.py
python -O analysis/check_v4160_peripheral_rx_ingress_static.py
```

一般／`-O` 均需精確重播 ledger，驗證 256 個 length-byte 投影、8,192 組 standard-ID 投影、512 個 queue／source 區間、四條 reader 路徑及 18 個指定原指令 mutation。這些是原指令靜態證據與主機算術，不是韌體、設備或 MMIO 功能測試。
