# v4.1.60：stack payload 的全域轉交與保存 callback 的實際消費端

本階段承接 [event/payload 呼叫鏈](v4160-event-payload-chain-static.zh-TW.md)，以原始 APP bytes 完整展開七個本體。`0xc776` 將來源交給 copy slot 後，轉交的是另一個全域輸出物件；`0x173ee` 則實際讀取、清除並尾跳保存的 callback word。這些是條件性靜態呼叫合約，不是 provider 身分、實際 RF 傳送或 ownership 的證明。

重播入口：[檢查器](check_v4160_payload_consumers_static.py)、[完整指令／CFG／stores ledger](v4160-payload-consumers-static.json)。只解析 bytes、建立局部控制流程圖及驗證主機端位元算術，沒有執行或模擬韌體、provider、callback、MMIO 或裝置。

## 完整本體與輸入身分

區間採半開表示法。檢查器逐條固定所有指令的運算、暫存器、立即值與分支目標，核對完整 bytes SHA-256、邊界、可達節點、無局部迴圈及所有 store；子呼叫正常返回僅是 CFG 的條件。

| 角色 | APP 區間 | bytes | 指令 | stores |
|---|---|---:|---:|---:|
| 輸出欄位更新 | `0xc6a8..0xc776` | 206 | 75 | 5 |
| stack 至全域轉交 | `0xc776..0xc798` | 34 | 13 | 1 |
| callback 完成出口 | `0x173ee..0x17442` | 84 | 29 | 5 |
| retry | `0x17442..0x17476` | 52 | 16 | 1 |
| transport task | `0x17476..0x174ee` | 120 | 43 | 3 |
| status callback | `0x174ee..0x1753a` | 76 | 22 | 0 |
| task／status 設定入口 | `0x175e8..0x17666` | 126 | 44 | 9 |
| 合計 | | **698** | **242** | **24** |

APP 為 76,800 bytes，base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。也重新驗證前階段的 APP、SDK header、兩個 resident 候選、完整 sparse HEX 覆蓋與 sidecar；候選資料仍僅作參考。未提高既有 C 重建覆蓋率。

## `0xc776`：原來源與輸出物件分開

入口 `A0` 是來源指標。`0xc788` 呼叫 fresh `[0x4004c]`，提出 `(A0=GP+220, A1=入口來源, A2=7)`，不測 scalar 回覆。隨後恢復 RA／SP，設定 `A0=0x2000c290`，在 `0xc796` 尾跳 `0xc6a8`。本體沒有直接將原來源存入 pointer field，但其他暫存器仍可能帶著來源指標：參考 copy 不改 A1，本體也未覆寫 A1，因此尾跳時 A1 仍可能是原 stack 來源。`0xc6a8` 本身不讀寫 A1，後續 `0x12a08` 是否觀察它仍未知；不能宣稱原指標不外傳或不保留。

只有實際 copy provider 符合參考實作、存取有效、所需 context 保存且無不利別名／介入寫入，才能將七個來源 bytes 與全域目的地連起來；不能據此排除 provider 保存原 stack 指標。名義 `GP=0x20004000` 時，全域封包 `P=0x200040dc`，輸出物件 `O=0x2000c290`，兩者不是同一指標。

## `0xc6a8`：重讀封包，局部寫入輸出物件

本體無 frame、無子呼叫，只寫 A2–A5 及五個 `O` 相對 byte stores；其餘出口為 RET 或 `0xc750` 尾跳 `0x12a08(O)`。

1. fresh `U32[P]` bit 9 為零就返回，不寫輸出。
2. 另讀 `U32[P]` bits 10–15；非零才組合另兩次 fresh loads：`(U32[P] >> 16) | ((U32[P+4] & 255) << 16)`，依序存低三個 bytes 至 `O+4..6`，記錄這條寫入路徑已執行。即使值相同也算執行。
3. fresh `U32[P+4]` bits 8–12 非零才更新 `O+7`。比較 10、比較 20、乘算各有獨立重讀；原低七位也另讀，高位取寫入前的 fresh `O[7]` bit 7。算術先截成 byte，再與 100 比較，不能把不同重讀自行合併。
4. 只有步驟 2 的 stores 已執行，或步驟 3 的更新路徑已執行，才讀 `O+2`。非零時，把 fresh `U32[P+4]` bits 13–14 放進 fresh `O[8]` 低兩位，保留其他位元，再尾跳 `0x12a08(O)`。`O+2` 為零不回滾已完成的欄位 stores。

若另有證據支持各次封包欄位穩定，可令 `n=(U32[P+4]>>8)&31`：

| 穩定 n | O[7] 低七位 |
|---|---|
| 0 | 不更新；依先前 stores 路徑決定是否檢查 O+2 |
| 1–10 | `min(100, low8((舊 O[7]&127)+10*n))` |
| 11–20 | `10*(n-10)` |
| 21–31 | 0 |

原指令允許不同重讀值。例如加法路徑中的後一次 n=26，可先算 `low8(260)=4` 再 cap，不能套用穩定欄位表。一般入口 O 也可能別名 P，穩定性必須另外證明。

`LW P+4` 讀到七個 copied bytes 之外的 `P+7`；本體選取的欄位沒有使用 P+6／P+7 的位元，但仍要求該 word 存取有效，不能宣稱第八個 byte 已初始化。`0x12a08` 收到 O，後續副作用與保存期尚未展開。

## `0x173ee`：先清控制欄位，再捕捉、清除、尾跳 callback

完整入口 A0 先保存至 S0；向 fresh `[0x4005c]` 提出 `(fresh U8[0x2000c7a0], 2)`，不測回覆。其後順序如下：

1. 清 byte `0x2000c7a8`。
2. 清 byte `0x2000c7a9`。
3. fresh load `U32[0x2000c7a4]` 至 T1。
4. raw T1 非零時，A0 換回保存的入口值，恢復 context，清 callback word `0x2000c7a4`，恢復 SP，於 `0x17438` `JR T1`，有效目標為捕捉值 `& ~1`，不寫新 RA。

callback 為零時直接返回，A0 不正規化，可能仍是 stop 請求的回覆。非零路徑不測 callback 回覆，且本體沒有 callback 返回後的清理段。這證明了保存 word 的實際條件性消費邊，不能在缺少欄位保存證據時認定其值一定是先前寫入的 `0x17666`。

capture／clear 不是原子操作，沒有證明 exactly-once 或重入安全。清控制 bytes 先於 callback，但沒有局部直接清除 `0x2000c7aa` 起的 header／payload。stop provider、IRQ、其他 writer 與 callback 自身的效果仍未知。

## retry、task 與 status 的相接出口

`0x17442` 先把 `u=(fresh U8[0x2000c7a8]-1)&255` 存回原 byte。u=0 時尾跳 `0x173ee(1)`；非零時尾跳 fresh `[0x40058](fresh task byte,1,2)`。原值 0 會回繞成 255，只有原值 1 產生零出口，不能宣稱有無條件重試上限。

`0x17476` 保存完整入口 A1 為 E，按低 16 位元檢查優先序：

| 優先條件 | 本機提出的呼叫 | 正常返回後 A0 |
|---|---|---|
| bit 15 | fresh `[0x4006c](入口 task)`；回覆非零才交 fresh `[0x40068](回覆)` | `E XOR 0x8000` |
| 否則 bit 0 | fresh `[0x401d0]`；再 fresh `[0x401cc](0x2000c7aa, fresh U8[0x2000c7a9],255,255)` | `E XOR 1` |
| 否則 bit 1 | `0x173ee(1)` | `E XOR 2`，覆蓋下游回覆 |
| 皆無 | 無 | 0 |

SDK aliases 對應 `RF_Shut`、`RF_Tx`；名稱與候選 slot targets 不是實際 provider 綁定或傳輸完成證據。

`0x174ee` 沒有局部 stores 或子呼叫：完整 A0=2 時，先要求 A1=0，再依序 fresh 比對 `U8[A2+1]==2`、`U8[A2+2]==U8[0x2000c7aa]`、`U8[A2+3]==U8[0x2000c7ab]`。全符合才尾跳 `0x173ee(0)`，任何不符尾跳 retry。沒有 A2 null／extent guard，也沒有 header 原子快照。

完整 A0<2 直接返回。其他狀態先計算 `A0=low8(A0-17)`，結果 <=1 才進 retry，否則以轉換後 A0 返回。因此完整狀態 273 也符合低 byte 17 的分類，不能只列完整狀態 17／18。

## `0x175e8`：task 與 status 入口的本機 literal 來源

48-byte frame 內先提出 fresh `[0x40048](0x2000c7a0,0,268)`；再提出 fresh `[0x40080](A0=0x17476)`，將回覆低 byte 寫入 `0x2000c7a0`，沒有 invalid-ID guard。接著提出 fresh `[0x40048](SP,0,32)`，依序建構：

| stack 位移 | 寬度 | 值 |
|---|---:|---|
| +8 | 4 | `0x8e89bed6` |
| +12 | 4 | `0x00555555` |
| +0 | 2 | `0x2501` |
| +16 | 4 | `0x174ee` |
| +25 | 1 | 4 |

最後以 A0=SP 呼叫 fresh `[0x401c4]`，SDK alias 為 `RF_Config`，回覆不檢查即恢復 frame。這關閉了 task／status 位址的本機常數來源，但未證明填零、註冊實際成功、provider 複製或保存 stack config，亦未證明其後真的呼叫 status callback。

## 驗證與仍開放的邊界

可用本機 Python 執行：

```text
python analysis/check_v4160_payload_consumers_static.py
python -O analysis/check_v4160_payload_consumers_static.py
```

兩種模式均重算並逐 byte 比對 ledger；驗證 65,536 組事件優先序、65,536 組 status 分類、256 個 retry byte、7,936 組穩定欄位算術，以及 18 個指定原指令 mutation 均由對應 operand guard 拒絕。這些是主機端的靜態證據完整性與算術檢查，不是韌體行為測試。

下一步是 `0x12a08` 的輸出物件消費／保存、RF_Config 的 stack config 合約、其他全域欄位 writers，以及實際 installed provider 綁定。所有跨未知子呼叫的資料關係仍依賴正常返回、必要 GP／S／SP／RA 與 frame 保存、有效存取、無不利別名及未計入的 IRQ／重入／介入寫入。
