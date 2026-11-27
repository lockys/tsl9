# v4.1.60 setup 下游：登記、RAM 派送、channel 與 reset 串接

接續[完整 setup 本體](v4160-b1-setup-full-static.zh-TW.md)。本輪將 setup 的三種下游呼叫，接到已核對完整原指令的 registrar、RAM dispatch、channel 與 reset。結論仍是兩版 **resident 參考候選**的條件性靜態合約，沒有認定實際 installed provider。

新的可驗證結論是：**setup 若正常返回，A0 可追到最後一次 RAM 派送內 channel 所讀取的完整 `U32[H0+12]`**。reset 不讀寫 A0，所以不會額外產生新的 status，也沒有把回覆改成固定 success。這個串接依賴對應的候選／搬移映射、有效存取、callee 正常返回、frame／register 保存及沒有破壞資料流的別名或非同步干擾；不等於硬體傳輸成功。

## 本輪範圍與重用

| 完整本體 | V131 入口 | V140 入口 | 每版 bytes／instructions | 既有原指令檢查 |
|---|---|---|---|---|
| registrar | `0x43b28` | `0x43bb4` | 22／8 | [hook sources](check_v4160_loaded_hook_sources_static.py) |
| RAM dispatch | `0x200026ba` | `0x20002706` | 250／93 | [constructor consumer tail](check_v4160_constructor_consumer_tail_static.py) |
| channel | `0x63b0e` | `0x63bf8` | 326／124 | [channel leaf](check_v4160_b1_channel_static.py) |
| reset | `0x63e58` | `0x63f42` | 130／48 | [RF tail return](check_v4160_rf_tail_return_static.py) |

合計重新核對 **1456 bytes／546 instructions**，全部已在既有 checkpoint 完整覆蓋；本輪新增的是跨函式呼叫／實參／返回資料流證書，**新增原始 byte 覆蓋為 0，APP C 重建覆蓋率不變**。沒有將重用本體算成新增反組譯覆蓋。

RAM 本體在候選 FLASH 的來源分別為 `0x4292a／0x429b6`。檢查器依 first-copy 的 source／destination 與末址，核對全部 250 bytes 落於搬移範圍內，再以 RAM PC 核對 call target；同時逐 byte 比對保留的 sparse HEX，缺口不以零補齊。其餘三種本體也核對完整 strict HEX、operands、hash 與 CFG。

## 登記的是 callback 指標，沒有呼叫 callback

setup `+0x344` 的 A0 是 literal callback `0x55480／0x5555e`，A1 在 `+0x308` 明確設為 0，且兩者中間沒有另一個可覆寫實參的 call。完整 registrar 只接受 unsigned index≤4；因此此處走 index 0 的 store 路徑：

```text
U32[0x200031c8 / 0x20003218] = 0x55480 / 0x5555e
```

registrar 無 nested call、無 frame，不改 A0、S registers、RA、SP、GP。它保存 raw callback pointer，**不會當場呼叫該 callback**。這個 slot 與其他 hook 槽分開；尚未證明登記順序、後續覆寫者、實際 table consumer、callback 執行時機或完整 referent 保存期。

## Setup 的兩次 RAM 呼叫都走零模式

setup `+0x358` 與 `+0x5a6` 各自傳入：

```text
A0 = 0
A1 = fresh U8[P+128]
A2 = separately fresh U8[P+17]
```

第二輪的 mode 與 length 不與第一輪共用快照；P17 也不是直接使用 earlier header register，而是重新讀取。按 A0=0 的明確來源，RAM `+0x10` 的 nonzero-mode branch 不取；完整 93-node CFG 保留，另輸出這次呼叫可進入的 **47-node 零分支**。RAM 的 mode1／mode3 分支沒有在這兩個 setup callsite 被證明可達。

RAM 先於 `+0x0c` 捕獲 `D0=fresh PTR[G+1340/1420]`（`G=0x20003000`），在 `+0x14／+0x16` 重讀 **held D0+100**，直到為零才前進。迴圈不重新載入 D0，沒有 timeout 或進展上限。

之後清 context C+2，保存入口 A1，再把入口 A1、A2 分別轉入 child A0、A1，於 `+0x2c` 呼叫 channel：

```text
channel(fresh setup U8[P+128], separately fresh setup U8[P+17])
```

channel 不使用入口 A2，因此這裡沒有把 inherited 第三實參當成資料指標。這不代表所有 target 資料來源已閉合：channel 與 RAM 都仍會讀取其他全域指標及欄位。

## Channel 的 byte mode 分類、算術與回覆

channel 本體本來使用完整 A0 比較 mode；本串接的 A0 由 U8 零擴充，故可限制於 0～255。令 `a` 為該輪重新讀取的 P17 byte，`s` 為 channel 獨立取樣的 context byte10：

| 當次 mode | byte mode 數量 | 寫入 duration 的 host 整數形式 | A0 的完整 word 取樣偏移 |
|---|---|---|---|
| 恰為 1 | 1 | `8*a + 2*s + 404` | `+0x4a` |
| 恰為 3 | 1 | `32*a + 2*s + 1304` | `+0xba` |
| 其餘且 bit1=0 | 127 | `16*a + 2*s + 476` | `+0x120` |
| 其餘且 bit1=1 | 127 | `128*a + 2*s + 1820` | `+0xee` |

例如 mode5 屬於 bit1=0 的 fallback，而 mode7 屬於 bit1=1 的 fallback；不能只用 mode 低兩位代替「恰為 1／3」的比較。以 a／s 的 byte 域，上式範圍包含於 404～34970，沒有因此證明硬體時間單位、有效 packet 長度或 buffer 容量。

每個 mode／descriptor 分支中，channel 都在 R+0 更新**之後**，從 `+0x36` 捕獲的 `H0=fresh PTR[G+1340/1420]` 讀取完整 U32[H0+12] 到 A0。接著按原指令遮罩 H0+12、重新載入另一個 H1 指標，寫 H1+8、duration 與捕獲的 word；A0 保留至兩個正常 RET 之一。H0 與 H1 不預設同一物件，也不把 H0+12 視為函式入口前的快照。

channel 無 nested call、無 frame、無 loop，不定義 S registers、RA、SP、GP；只使用已核對的 caller-saved registers。fresh descriptor 槽非零時的兩個 pointer OR stores 仍保留，沒有套用其他舊路徑的 descriptor=0 假設。

## RAM 返回與第二個等待區

channel 返回後，RAM 仍會對 fresh R 做欄位更新、清 C+5 與 C+1，向重新取樣的控制物件寫 word0=2。於 `+0x58` 捕獲另一個 `D2=fresh PTR[G+1340/1420]`，之後的等待依序重讀：

1. fresh U8[C+2] bit0；設置就退出等待。
2. fresh U8[C+3] bit0；設置就退出等待。
3. U32[held D2+100]；為零就退出，非零則回到第 1 項。

兩個前置 byte 判斷是獨立讀取，並非原子快照。RAM 的零分支恰有兩個 cyclic SCC：`+0x14/+0x16`，以及 `+0x64..+0x72`；沒有證明 writer／IRQ 一定更新它們。即使 channel 已正常返回，RAM 也可能停在後面的等待，不能據此保證 setup 已返回。

從 channel call 到 RAM `+0x7c` RET，A0 沒有新定義，因此保留 channel 回覆。RAM 的 16-byte frame 保存並恢復 RA、S0、S1；其他 S registers 與 GP 沒有 encoded 定義。指令與 save／restore 配對不替代有效 frame、無破壞性 alias、呼叫保存和正常存取的前提。

## Reset 與 setup 最終返回值

完整 reset 只定義 A2～A5，不讀寫 A0，無 call／frame，唯一 RET 在 `+0x80`。本體先對持有 T 做兩次更新，依重讀的 bit3 跳過或執行四個 NOP，再更新 R+0、U+8、從槽位重讀 T 後清 T+80，最後清 context byte7。fresh descriptor 槽非零時另有兩個 pointer OR stores，不能宣稱對其他 RAM 物件完全無害。

這修正了先前把 setup `+0x360` 當成 opaque A0 新來源的界線：匹配的 reset leaf **透傳呼叫前 A0**。將此 no-write 合約接回 setup CFG，唯一正常 RET `+0x38c` 的 A0 最近來源縮小為 RAM call `+0x358／+0x5a6`：

```text
第一輪 RAM -> channel full U32[H0+12] -> RAM RET -> reset 不改 A0 -> setup RET
後續輪 RAM -> 該輪 channel full U32[H0+12] -> RAM RET -> setup RET
```

若 setup 重複進入後續輪，每輪 RAM 回覆會取代前一輪；正常返回時保留最後一輪的取樣。setup、RAM、channel 的各種等待／存取／非同步前提仍存在。這個完整 word 不是 duration、已複製 byte 數、固定 success、硬體完成確認或 payload ownership token。

## 驗證與尚未閉合的條件

[檢查器](check_v4160_b1_setup_services_static.py)與[固定 ledger](v4160-b1-setup-services-static.json)保存完整重用本體、strict HEX、搬移來源、兩個 callsite 的 reaching definitions、零分支 CFG、兩個等待 SCC、八條 mode／descriptor 路徑、word 回覆來源，以及 reset 後的 A0 追蹤。使用一般模式與 `-O` 逐 byte 重建固定 ledger，並拒絕 **546 個逐指令突變／40 個 load 型別突變**；262144 個 mode／header byte／s 邊界組合只在 host 整數上核對，沒有建立 target RAM、packet 或 IRQ 模型。

```powershell
python analysis/check_v4160_b1_setup_services_static.py
python -O analysis/check_v4160_b1_setup_services_static.py
```

全程沒有執行或模擬目標韌體、接觸硬體、送出封包或進行 target network 操作。尚需確認實際 installed provider 與登記順序、callback table 消費端、P76／P168 等 buffer 的配置與容量、別名／其他 writer、等待進展，以及完整消費釋放與指標保存期。
