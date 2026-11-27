# v4.1.60：B1 buffer 的條件性來源、範圍與保存界線

這次把 APP 設定副本、RF 指標發布、heap 邊界及 completion 清理後的讀取接通，回答「callback 使用的 P，是否就是 cleanup 釋放的物件」。目前只能給出條件性來源與區間證明，尚不能證明實際指標互不相同或完整保存期。

[驗證程式](check_v4160_b1_buffer_origin_static.py)與 [JSON ledger](v4160-b1-buffer-origin-static.json)重新核對既有完整函式、原始 operands、SHA-256、strict sparse HEX 與有限區間算術。沒有執行或模擬目標指令、allocator、provider、packet 或可變 RAM 狀態，也沒有操作硬體。

## 來源鏈：APP literal 經設定副本到 S+36／S+32

APP 完整 builder `[0x199e2,0x19b16)` 為 308 bytes、106 指令。其中 `0x19a3a..0x19a4a` 的 16-byte 子範圍已包含於 builder，不重複計數：

- `0x19a3a/0x19a3e` 組出靜態 literal **H=0x2000418c**。
- `0x19a42` 把 H 寫到 SP+16；`0x19a46` 把長度 halfword **L=0x7000（28,672）**寫到 SP+20。
- `0x19aea` 將 SP+16 作為參數，`0x19aec` 透過 fresh 400a4 槽位呼叫設定服務。

H 是 APP 提供的設定基址，並非本階段觀察到的 allocator 回傳值。完整候選 400a4 initializer 先清零 64-byte 設定區，再要求 copy `(destination,config,64)`。其後已定位的直接 default stores 不寫 word0；optional callback、巢狀 callee、外部 writers 與實際 copy 綁定仍需另行保存假設。

| 完整既有函式 | V131 候選 | V140 候選 | 每份 bytes |
|---|---|---|---:|
| 400a4 設定 initializer | 0x43c7e | 0x43d0a | 228 |
| RF 指標 publisher | 0x64298 | 0x64382 | 118 |
| heap bootstrap | 0x43104 | 0x43190 | 112 |
| C+4 配置與替換 | 0x64bae | 0x64c98 | 318 |
| inner cleanup | 0x656c6 | 0x657b0 | 148 |
| completion callback | 0x65de6 | 0x65ed0 | 430 |
| first-copy copy helper | RAM 0x20000332 | RAM 0x20000332 | 58 |
| first-copy fill helper | RAM 0x2000039c | RAM 0x2000039c | 46 |

V131 設定目的地為 `0x200031ec`，S=`0x20003514`，C=`0x20003560`；V140 對應三者各加 80。RAM helpers 的完整來源依各自 first-copy affine mapping 核對，這不等於證明目前已安裝該候選。

RF publisher 從設定區 word0 **重新載入 X**，寫出 `S+36=X`，再寫 `S+32=low32(X+272)`；後面還有三個呼叫／尾跳。因此，僅在設定複製正確、word0 及相關狀態一路保存的條件下，才能把數值串成：

```text
APP H=0x2000418c → resident config word0 → fresh X
S+36 = X        → nominal 0x2000418c
S+32 = X+272    → nominal 0x2000429c
```

completion 在不同位置 fresh load S+36，服務輸入與後來保存在 S0 的 P 不能逕視為相同觀察值。更不能只由發布時的來源，推定後來讀到的指標仍等於 H。

## 272+272 的幾何證明，不是資料長度證明

完整 bootstrap 使用 fresh config H／L，第一個 small-heap header 位於 H+544；split 為 `min(L>>3,512)`。若沿用上述名義 H／L，得到以下半開區間：

| 用途／邊界 | 名義位置 | bytes |
|---|---|---:|
| S+36 指向的前綴 | `[0x2000418c,0x2000429c)` | 272 |
| S+32 指向的前綴 | `[0x2000429c,0x200043ac)` | 272 |
| small header | 0x200043ac | — |
| large header | 0x200045ac | — |
| sentinel | 0x2000b184 | — |
| 設定區間終點 | 0x2000b18c | — |

callback 直接讀取至 P+26，因此最小所需 extent 是 27 bytes；comparator `(P+9,...,6)` 及 copy `(...,P+3,6)` 的數值區間也落在首個 272-byte 前綴內。S+32 的 word0 寫入落在第二個前綴內。

這只證明「若指標仍等於名義來源，相關存取在數值前綴中容得下」。沒有因此證明 ingress 真實長度至少 27、資料已初始化、硬體有寫入、buffer 實際配置成功或存取期間內容不變。前綴位於首個 heap header 之前，也不代表已證明 allocator 的完整現行不變量。

## C+4 的來源及 cleanup 後 P 的界線

C+4 是另一個槽位：RF 配置函式釋放先前擷取的 C+4、清零該槽，再要求 allocator `(2+freshU8[F+29],73)`，把回傳 A0 寫入 C+4，沒有就地 null guard。一般 byte 域的要求大小為 **2..257**；僅在 APP default F+29=251 一路保存的條件下，名義要求才是 **253、tag 73**。

inner cleanup 重新載入 C+4，非零時要求 private release `0x20000110`，再清零 C+4。completion 先將 fresh S+36 保存在 S0，呼叫 cleanup，返回後仍從 P+19 等位置載入內容。這段順序已由完整 callback 與 cleanup 原指令核對。

**槽位不同，不足以證明指標值不同。** H literal 與 allocator reply 的來源不同，也不足以排除別名。S0 暫存器保存 P 的數值，更不足以證明 P 所指物件在 cleanup 後仍有效。

區間證書檢查了 `[H+544,H+L-8)` 的 **28,120 個整數地址**全部位於兩個前綴之外。只有再證明 C+4 確為目前有效配置、整個 payload 位於這個受管理區間，且 S+36 保持 H，才能用此排除本次 release 的物件與前綴重疊。這些 ownership、實際 allocator 域、writers 與保存條件尚未建立，故不宣稱安全釋放或釋放後使用問題已成立。

## 驗證與仍未完成的事項

本次重驗唯一完整函式共 **3,224 bytes**：APP 308 bytes，加上兩份候選各 1,458 bytes。**新增原指令函式 0 bytes／0 指令**；這是來源與保存界線的串接，不增加既有 C 重建覆蓋率。

37 個原始 source／publication／C+4／free operand mutation 均由完整函式 guard 拒絕；strict HEX 禁止補零洞。一般與 `-O` 模式必須逐 byte 重放同一 JSON ledger；上游完整證據鏈亦重新驗證。

```powershell
python analysis/check_v4160_b1_buffer_origin_static.py
python -O analysis/check_v4160_b1_buffer_origin_static.py
```

後續仍須定位 P／S+36 的其他 writers、真正填入 byte 內容的 producer、實際 ingress 長度與初始化條件，以及 C+4 當前 ownership。實際 provider／callback 綁定、callback 派送相對外層 C+12 清零的順序、polling 進展及完整指標保存期也仍未證明。
