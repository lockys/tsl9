# 0x5d006 setup 前段：物件欄位、共享指標與範圍呼叫

沿 [BB handler 的共享指標](v4160-b1-bb-irq-static.zh-TW.md) 往 producer 查，本輪首次展開 setup `0x5d006／0x5d14e` 的入口至第一個條件分支：兩版各 **238 bytes／83 條指令**，合計 **476 bytes／166 條新前段指令**。

這是有明確出口邊界的 prefix，**不是整個 setup 函式**。LLE 零／非零 callees 已有完整證據，本輪未重新計數。[Python checker](check_v4160_b1_setup_entry_static.py) 與 [固定 JSON ledger](v4160-b1-setup-entry-static.json) 保存 operands、來源 hashes、選定 CFG、兩條語法出口路徑、caller 定義來源與條件性 helper 合約。所有分析僅讀原始 bytes／strict sparse HEX，沒有目標執行、模擬、可變 provider／IRQ／物件模型或硬體操作。

| 候選 | 新 prefix | 未展開的兩個出口 |
|---|---|---|
| V131 | `[0x5d006,0x5d0f4)` | `0x5d0f4`、`0x5d128` |
| V140 | `[0x5d14e,0x5d23c)` | `0x5d23c`、`0x5d270` |

## Caller 明確傳回入口物件

重用 [B+120 callback target](v4160-b1-b120-target-static.zh-TW.md) 的完整 1000-byte 本體。它在 `+0x18` 把入口 A0 存入 S0；在先前 callee 正常返回後，`+0x306` 明確執行 `A0=S0`，`+0x308` 才呼叫 setup。

完整 CFG 的 reaching-definition 核對顯示，該位置的 S0 來自 `+0x18`，不來自 epilogue restore。故在各 callee 遵守 S0／SP／saved frame 保存條件時，setup 收到的是 caller 的入口物件 P，並非上一個 callee 的回覆。這不證明 P 的實際配置、存活或此前釋放歷史。

## 第一個呼叫之前：192-byte 直線區段

setup 配置 **80-byte frame**，保存 RA 及 S0..S11 共 13 個 word。`+0x38` 將入口 A0=P 存入 S8，之後 A0 才被改作常數／helper 參數。首個 linked call 在 `+0xc0`，此前沒有分支或子呼叫。

令 G=`0x20003000`，固定槽位如下；T／R／U 是各自讀出的 pointer，H 是固定 context base：

| 角色 | V131 | V140 |
|---|---|---|
| T 槽 | G+1340 | G+1420 |
| R 槽 | G+1288 | G+1368 |
| U 槽 | G+1424 | G+1504 |
| H | G+1300 | G+1380 |

T／R 槽與 BB handler 相同，H base 亦相符；但各次 fresh 讀值不因此相同，也沒有證明載入的 pointee 彼此分離、等同或保持有效。U 為另一個來源槽位。

第一個呼叫前，13 個非 frame store 的順序為：

```text
T+100 = 160
R+44  = (fresh word & ~3) | 1
R+0   = fresh word & ~0x180
R+0   = (另一筆 fresh word & ~0x180) | 0x100
U+8   = fresh word | 0x00330000
T+80  = 90
U+44  = fresh word & ~2
R+0   = (fresh word & ~127) | (fresh U8[P+126] & 127)
T+4   = fresh word & ~1
R+44  = (fresh word & 0x81ffffff) | ((fresh U8[P+104] & 63) << 25)
R+8   = fresh U32[P+140]
R+4   = fresh U32[P+144]
byte[H+3] = 0
```

R+0 的兩個前置 store 使用不同 fresh samples；R+44 也在另一時點重新讀取。它們不是原子更新，更不代表硬體模式或中斷效果已被驗證。R+44 的 mask 排除 bits25..30，讓 P+104 的低六位填入該欄位；bit31 與 bits0..24 在這個數值運算中保留。

這段只直接讀 P 的四個欄位：U8[P+126]、U8[P+104]、U32[P+140]、U32[P+144]。沒有 P null／extent guard；部分 T／R／U store 發生在第一次 P 欄位讀取之前。

在第一個 call 前，沒有把入口 A0 的來源直接當作指標發布；但欄位內容、pointee 別名或既有 S-register 值可能有其他關係，不能據此宣稱整條鏈不保存 P。

## 第一個 helper：固定實參 1、35，正常回覆 1–34

`+0xc0` 呼叫 `0x43e6a／0x43ef6`，A0=1、A1=35。其他 then-live 暫存器不是清零的，載入的 R 也不保證與 P 分離。

重用 [完整 byte-range helper](v4160-comparator-tail-static.zh-TW.md) 的 36-byte 本體及 [108-byte source](v4160-range-retry-static.zh-TW.md)。在 matching code 正常返回、source／frame／S0 等保存條件成立時，其算術為：

```text
r = source 的 U32 回覆
result = low8(1 + floor(34*r / 2^32))
```

因 `0 <= r < 2^32`，`0 <= floor(34*r/2^32) <= 33`，故正常回覆介於 **1–34**，低八位截斷不改變它。這不證明分布均勻、所有值實際可達，或 nested clock／source 會終止；S8 與 caller frame 在呼叫期間的保存也仍是條件。

## 呼叫後：P+126 改值，Q header 初始化

若 helper 正常返回且保存所需暫存器，後續直線區段為：

```text
Q = fresh U32[P+76]
byte[P+16]  = 7
byte[P+126] = low8(helper reply)
byte[Q+0]   = 7
byte[Q+3]   = 0
byte[Q+2]   = 1
取樣 fresh U32[P+84] 的 bit9，進入第一個條件分支
```

Q 沒有 null guard、長度檢查或本機配置。整個 prefix 的直接 P 存取至少需要 148 bytes，Q 的顯式存取至少需要 4 bytes；這些只是所需 extent，不是實際 buffer 大小或存活證明。

**R+0 的低七位先取自呼叫前的 P+126，P+126 隨後才被 helper 回覆覆寫。** 即使忽略其他 writers，也不能自動把後來的 P+126 與先前 R+0 值視為同一份設定。

第一個條件分支只檢查 fresh P+84 bit9。兩個 prefix 出口都仍有 80-byte frame 存活，沒有在此看到 RET／frame 還原；未展開的 optional cases、後續 calls、完整返回及 payload 保存期仍待追查。

## 驗證

```powershell
python analysis/check_v4160_b1_setup_entry_static.py
python -O analysis/check_v4160_b1_setup_entry_static.py
```

完整 prefix 有 31 個 stores：13 個 frame saves、13 個 first-call 前的其他 stores、5 個 call 後 stores。兩條語法出口路徑涵蓋全部所選 CFG edges，不是目標執行軌跡。

負向核對包含 **166 個逐指令變異、18 個 typed-load funct3 變異**。純 host 整數核對包含 131072 個 source-reply 邊界族樣本及全部 256 個 byte 欄位；範圍結論另由非負單調算術邊界支持，未把樣本說成所有 U32 的窮舉。原有驗證鏈、輸入身份、strict sparse HEX 與固定 ledger 也一併重跑。

本輪增加新 prefix 靜態證據，`new_complete_body_bytes=0`，APP C 重建覆蓋不變。實際 provider、R／T／U pointee、IRQ 順序、Q 來源與完整消費釋放保存期仍未完成驗證。
