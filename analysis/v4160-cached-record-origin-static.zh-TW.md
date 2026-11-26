# v4.1.60：length／tag 的 row18 來源與初始化邊界

承接 [tagged 路徑與兩次長度讀取](v4160-tagged-dispatch-static.zh-TW.md)，已找到快取物件 `O=0x2000c290` 的具體 producer：mode 1、取樣 ID=1657 的分支，向 copy slot 提出把原 record P 的 12 bytes 存入第 18 列的請求。這包含 `O+2` 的 length 與 `O+11` 的 tag；本地 case 沒有檢查這兩個來源欄位。

另一個重要區別是，copy 正常返回後立即尾跳的是 `0xc6a8(P)`，不是 `0xc6a8(O)`。稍後的 `0xc776` 路徑才明確使用 O。不能把原 record 與快取 record 的修改、派送或保存期合併。

本次只解析 bytes、核對 operands／局部 CFG／範圍及主機算術；沒有執行或模擬 target ISA、copy、reset、RAM／stack、provider 或 MMIO。[檢查器](check_v4160_cached_record_origin_static.py) 與 [證據 ledger](v4160-cached-record-origin-static.json)。不增加既有 C 重建 bytes 或覆蓋率。

## 已核對的範圍

| 類別 | APP 範圍，半開 | bytes／指令／stores |
|---|---|---:|
| 完整 mode getter | `0x829e..0x82a8` | 10／3／0 |
| 完整 row wrapper | `0x82a8..0x82d2` | 42／16／0 |
| 外層 mode 派送前綴 | `0x14d2e..0x14d52` | 36／14／2 |
| ID 819 節點 | `0x14d5e..0x14d6e` | 16／4／0 |
| ID 991 節點 | `0x14ed8..0x14ee4` | 12／3／0 |
| ID 1025 節點 | `0x14fa0..0x14fac` | 12／3／0 |
| ID 1267 節點 | `0x15002..0x1500e` | 12／3／0 |
| ID 1657 節點 | `0x15032..0x1503a` | 8／2／0 |
| row18 寫入 case | `0x152ba..0x152d0` | 22／9／0 |
| 初始化前綴 | `0x12d92..0x12dc0` | 46／16／2 |

完整兩個本體合計 **52 bytes／19 指令**；八個明示有界窗口合計 **164 bytes／54 指令／4 stores**。每個窗口全數 operands、bytes hash、邊界與局部可達節點固定。未把這些窗口當成完整 `0x14d2e` 或 `0x12d92` 函式；所有離開窗口的分支／接續仍列於 ledger。

另重新核對既有完整 reset 的 138 bytes／37 指令，以及前階段來源鏈。APP 為 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。resident 候選身分與 sparse 覆蓋仍只是參考證據，不等同 installed provider。

## mode 1 與 ID 1657 的選定路徑

`0x829e` 以 fresh `U8[0x2000bfb5]` 返回 mode。外層先保存 S0／RA，令 S0=P；mode<=6 才查原七項表 `0x1a6b8`。本階段固定完整 28-byte 表內容，核對 mode=1 的相對 word 指向 `0x14d5e`。

在 mode=1 且表／context 未受損的限定下，先 fresh 讀一次 `U16[P]` 到 A5。選定路徑不再改 A5，依序滿足：

```text
ID !=819  且 ID>819  →14ed8
ID !=991  且 ID>991  →14fa0
ID !=1025 且 ID>1025 →15002
ID !=1267 且 ID>1267 →15032
ID ==1657           →152ba
```

檢查器核對這些實際分支的 operands／targets，並對全部 65,536 個取樣 ID 驗證其交集只有 1657。這不代表 mode 一定為 1、實際 ingress 已到達，也不代表之後 copy 時來源 ID 仍保持 1657。

## row wrapper 與原 record／快取的區別

`0x82a8` 先 fresh load `[0x4004c]` 至 T1，取完整入口 A1=index，以 RV32 模數算術建立：

```text
R = 0x2000c1b8 + 12*index   （截為32 bits）
入口 A0=0：   tail T1(A0=R,        A1=入口A2, A2=12)
入口 A0非零：tail T1(A0=入口A2, A1=R,        A2=12)
```

本體沒有 frame、call 或新 link，也沒有 index、null、extent guard。index 未被限成 byte；例如 18、`0x40000012`、`0x80000012`、`0xc0000012` 均在模數乘法後形成相同的 R。這是一般 wrapper 的算術，非真實 caller 可達值證明。

選定 case 明確使用 index=18：`0x2000c1b8+18*12=0x2000c290`，目的範圍為 `[O,O+12)`；index=19 則已從相鄰配置 `0x2000c29c` 開始，wrapper 自身不排除它。

| PC | 本機動作 |
|---|---|
| `0x152ba` | A2=S0，即 P |
| `0x152bc` | A0=0，選寫入方向 |
| `0x152be` | A1=18 |
| `0x152c0` | JAL `0x82a8`，link=`0x152c4` |
| `0x152c4` | A0=then-live S0 |
| `0x152c6..0x152ca` | 恢復保存的 S0／RA／SP |
| `0x152cc` | 尾跳 `0xc6a8` |

copy scalar 回覆沒有被檢查。只有 provider 真正符合參考 copy、正常返回且保存必要 S0／frame、來源及範圍有效、無不利別名／介入寫入等前提，才可把 P+2／P+11 的 byte 與快取 length／tag 連起來。不能從這段無欄位 guard 推論真實 ingress 能提供全部 byte 值，也不能從返回值推定複製成功。

在上述 context 前提下，最後 A0=P；`0xc6a8` 的直接 stores 僅落在其 A0 相對 +4..8，所以這次更新的是 P。快取 O 是較早 copy 請求的目的地，不能自行當作同一個物件。兩個實體可能別名也需另外處理，未主張全域唯一 owner。

## reset、19-row 初始化與相鄰配置

既有 reset 的名義 zero 區間是 `[0x20004080,0x2000c958)`。在該程式、位址／存取與正常完成的條件下，word stores 於 `0x2000c290`、`0x2000c294`、`0x2000c298` 覆蓋整個 O，初次 length／tag 因而為零。這不是後續派送時仍為零的 invariant。

`0x12d92` 初始化前綴依序提出兩個 fresh fill-slot 請求：

| call PC | 參數 | 名義目的半開區間 |
|---|---|---|
| `0x12dac` | `(0x2000c038,0,384)` | `[0x2000c038,0x2000c1b8)` |
| `0x12dbe` | `(0x2000c1b8,0,228)` | `[0x2000c1b8,0x2000c29c)` |

第二個範圍恰為 19×12 bytes，包含 O 的全部 12 bytes；第一個範圍結束於 table 起點。它們仍是服務請求，不能宣稱實際清零或執行時序已觀測。第二次 slot load 依賴前次 callee 保存 S0，兩次 fresh word 也不保證相等。

reset 的 128-byte initialized-data source 從 APP `0x1ab60` 起。其中 `0x1abb4` 的 word `9c c2 00 20` 對應名義 `GP+84=0x20004054` 的初始值 **`0x2000c29c`**；它指向 O 結尾之後的配置，不是 O。不能把以該配置為起點的 112-byte 載入當成 O 的 producer，或將 fresh GP pointer 一直當成初值。

## 後續消費與仍需的保存條件

稍後的 `0xc776` 明確把 A0 設為 O，再進 `0xc6a8`。其 copy7 請求名義目的為 GP+220，沒有直接指定 O；`0xc6a8` 本身只直接改 A0+4..8，不寫 length+2／tag+11。

若 O 欄位在這段已知本機流程中保持、stack／MMIO／copy 範圍沒有不利別名或其他寫入，則：

- `0xc6a8(O)` 讀到非零 length 才可能繼續派送。
- tagged 路徑的初次長度檢查再把接受值限制為 1..8，且其初次 tag 要為 1／2。
- 後次 L1=L0 仍需跨 copy provider 與其他 calls 的物件保存／不干擾前提，不能從首次 <=8 自動得到。
- tag=0 的另一條路徑仍沒有自己的長度上限；實際來源與可達值尚未由本階段閉合。

## 候選掃描的範圍與重播

另掃 APP 所有半字 offsets，僅辨識相鄰 LUI／AUIPC 後接 standard ADDI／load／store 或 C.ADDI／C.LW／C.SW 的指定語法域。起址落在 O 內或所列寬度跨入 O 的候選只有 `0xc78c/0xc790` 形成 O；沒有掃到 O、O+2、O+11 的原始半字對齊 word literal。

這些候選不保證真實指令邊界或可達性；未涵蓋任意非相鄰地址形成、computed pointer、bulk writer、別名、provider 或 IRQ。已找到的 row18 間接複製正是不能靠「沒有固定 store 命中」排除 writer 的例子。

```text
python analysis/check_v4160_cached_record_origin_static.py
python -O analysis/check_v4160_cached_record_origin_static.py
```

兩種模式均需精確重播 ledger，通過 65,536 個 ID 交集、19 列區間、四個完整 index 別名及 18 個指定原指令 mutation 的 operand guard。source／candidate／sparse 與前階段合約也重新核對，沒有執行 CPU fixture。

下一步是 ID1657 的真實 ingress record、其 length／tag 的上層 guard、其他快取 writers／callback 時序，以及實際 copy／fill provider 的身分與保存期。此處沒有主張完整 writer census 或裝置功能成功。
