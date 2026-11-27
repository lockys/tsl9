# v4.1.60：list 直接 callbacks 與跨事件保存界線

這一階段把既有的「installer 寫入 B+112／B+116 → handler 的 bit0／bit1」接到兩個完整本機函式。新增原始指令證據合計 **1,460 bytes／506 條指令**，並未重算既有 C 重建覆蓋率。

分析對象仍是兩份 resident **參考候選**。APP、候選檔、SDK 與官方 Xwchc 指令欄位來源均重新核對；這些靜態對應不代表原裝置已安裝或實際呼叫此 provider。全程沒有執行或模擬目標指令、callback、裝置、MMIO、CSR 或傳輸。

| 完整函式 | V1.31 範圍（不含尾端） | V1.40 範圍（不含尾端） | bytes／指令數 |
|---|---|---|---|
| B+112，handler bit0 | `558a8..55b42` | `559e0..55c82` | 666／229；674／231 |
| B+116，handler bit1 | `550cc..55108` | `55196..551d2` | 每版 60／23 |

完整 SHA-256、逐條欄位、local CFG、call／tail 清單及重播結果見 [機器可讀證據](v4160-list-direct-callbacks-static.json)。bit1 結束後的 lookup `55108/551d2` 已有先前證據，不納入本次新增範圍。

## 從 handler 到物件

沿用 [setup 與 handler 證據](v4160-list-setup-handler-static.zh-TW.md) 及 [installer／creator 證據](v4160-list-origin-static.zh-TW.md)：B 是 `200033b8/20003408`；若 installer 的值確實保存到事件處理時，B+112 對應 bit0 本體，B+116 對應 bit1 本體。handler 本機保持 A0 為原 task 值、A1 為原完整 mask，且不以 callback 回覆決定自己的 mask XOR 結果；仍需要 callback 保存 S0、SP、frame 等前提。

本文件以下以 N 表示 callback 原先取出的物件指標，不預設它等同特定 creator 的存活配置結果。

| 項目 | bit0 | bit1 |
|---|---|---|
| N 來源 | fresh `U32[B+88]` | fresh `U32[B+100]` |
| 首次 N 存取 | null guard 後讀 `U8[N+12]` | **沒有 N null guard** 就讀 `U8[N+12]` |
| 本機最小直接存取範圍 | 至少 176 bytes，包含 N+172 的 word | 至少 13 bytes |
| frame | 16 bytes，保存 RA、S0、S1、S2 | 16 bytes，保存 RA、S0 |
| 持續狀態的直接寫入 | B+0／B+100／B+124、N 內欄位 | 無；只有 frame stores |

bit0 在通過前置 gates 後，先把**原 N 寫入 B+100**，後續 bit1 才會重新讀這個槽位。這證明一個候選寫入者與消費者的連接；沒有證明事件順序、N 在尾跳後仍存活、B+100 未被其他 writers 改寫，或 bit1 的未檢查指標必然有效。

先前 creator 的 192-byte 配置請求涵蓋這次的 176-byte 本機存取需求，僅是大小相容。實際配置大小、同一物件身分、非別名、callee 副作用與存活期仍需分別證明。

## bit1：條件呼叫與共用尾跳

若 N+12 不等於 1，恢復 frame 後直接返回；本機未替 A0 指定固定狀態值。

若 N+12 等於 1：fresh `U8[B+124] == 4` 時呼叫 `53d98/53e4a(N)`；其他值跳過。兩條路都把 A0 設成原 N，恢復 frame，再尾跳至 `54c08/54cd2(N)`。不能從 optional call 的回覆推導最終結果：回覆先被原 N 取代，而共用尾跳的結果、返回與保存期尚未封閉。

## bit0：發布、欄位更新與版本差異

N 為 null 或 N+12 不等於 1 時，不進行 nested calls。通過後，對 `2000351b/2000356b` 的 byte 做**三次獨立 fresh reads**，依序比較 5、3、11；任一當次讀值命中就恢復 frame，尾跳 `4354a/435d6(fresh gate byte, 1)`。未證明中間無干擾前，不能把三次讀取合成單一狀態快照。

其他路徑以 `U16[N+32]` 作 signed DIV 的分母，分子為 1600；將 fresh B+0 加一並截為 byte，依序發布 `B+100=N`、寫回 B+0，再比較計數與 DIV 回覆。需要服務時呼叫 `43edc/43f68`，返回後把 B+0 清零。分母在本機沒有 zero guard；65535 個正值分母的整數證據不涵蓋零。沒有為這些數值指定時間單位或實際可達範圍。

若 fresh N+14 等於 7，還會讀 N+105 與 `U16[N+112]`：

- N+105 非零且 counter 已達該 byte 限制：N+23=67；呼叫 `6a7cc/6a9b0(67, U8[N+8], 0, counter低8位)`，再尾跳 `55330/553fa(N)`。
- counter 低於非零限制時才增加 N+112；N+105 為零則跳過比較與增加。
- 未走上述尾跳時，V1.31 將 N+98 設成常數 5；**V1.40 改成呼叫 `43ef6(1,35)`，再保存回覆低 8 位**。這是新增服務與保存前提，不只是位址重定位。

繼續時 B+124=1。N+24、N+15 與 optional `433a8/43434` 的回覆低兩位決定 N+10／N+25／N+26：

| 分支 | N+10 | N+25 | N+26 |
|---|---|---|---|
| N+24=3，回覆低兩位=0 | 39 | 37 | 38 |
| N+24=3，回覆低兩位=1 | 38 | 37 | 39 |
| N+24=3，回覆低兩位=2 或 3 | 37 | 39 | 38 |
| N+24=2，N+15 bit0=1 | 37 | bit1 ? 38 : 39 | 0 |
| N+24=2，N+15 bit0=0 | 38 | 39 | 0 |
| 其他 N+24，N+15 非零 | bit0 ? 37 : bit1 ? 38 : 39 | 0 | 0 |
| 其他 N+24，N+15=0 | 更新後 N+25 | 輪替結果 | 0 |

最後一列精確轉換：舊值 0..36 → 37、37 → 38、38 → 39、39..254 → 37、**255 → 0**。加一先截為 byte，才比較是否超過 39，因此不能無條件宣稱結果總在 37..39。checker 覆蓋全部 256 個舊值。

## scheduling、copy 與後續 clock 邊界

再次 fresh 讀 N+14 及 gate byte。N+14=1 時，以 `43728/437b4(gate,1,U16[N+32])` 呼叫；其他值先呼叫 `43e6a/43ef6(1,14)`，將**完整回覆**加上 fresh N+32 halfword，以 32-bit wrap 結果作第三參數。未證明服務回覆、排程成功、延遲為正或實際排程入口。

接著依序檢查 N+53 的 bit1、N+60 非零、P=`U32[N+48]` 非 null、`U8[P+10]` 非零。全部通過則 N+52=2，再請求 RAM `20000332(N+54,P+12,6)`；任一失敗則 N+52=1。P 的 null guard 在 byte 存取前，但 copy 請求仍需要 P 至少 18 bytes 的可讀範圍。參考 copy 的既有證據不能自行確定實際 provider、同步完成或不保存借用指標。

fresh N+124 <= 2 時恢復 frame，尾跳 `54c08/54cd2(N)`。較大時：

- 先取 O=`U32[N+172]`，**沒有 O null guard** 就讀 O+10；兩個後續分支均需要至少 11-byte 可讀 O。
- 從 `200031e0/20003230` 載入函式到 A2；兩個 callsites 均**沒有 function null guard**。call 前沒有重新設定 A0，不能推定這是無參數服務。
- O+10 非零：令 C=`20003234/20003284`，duration=`(U8[O+9]*U8[O+5]*U16[C+8]+400)//800`。依欄位寬度，分子最大 4,261,413,775，沒有 32-bit 乘加溢位，duration 最大 5,326,767。之後 N+148 的加法、C+4 的單次修正及 clock 回覆差值均依 32-bit wrap 計算。
- O+10 為零：取 N+152 的 word，呼叫該服務；若小於回覆就加 fresh C+4 一次，再比較差值。

兩條 clock 分支最後均以 unsigned 差值比較 fresh `U16[N+118]`；達門檻就尾跳 `54c08/54cd2(N)`，否則本機返回。單次加減修正不等同已證明一般模數運算、clock 單調性或週期範圍。不論 local CFG 無循環，未知 callees／tail 是否返回、是否改寫或釋放 N，仍需追查。

## 外層物件 writers 的下一個定位點

獨立的只讀原始 bytes 檢視另定位到 B+128 constructor `5e8bc/5e9a6` 與 B+148 constructor `57cbe/57dfe`。候選配置請求分別為 232／160 bytes，發布 outer pointer 早於 callback 欄位寫入，配置失敗路徑則保留舊槽位。這些是**下一階段完整 operand／CFG 驗證入口**，沒有列入本次 1,460 bytes 或 506 個 operand guards，也未宣稱已封閉所有 writers、實際 caller、發布順序的並行效果或物件保存期。

本次兩個 callbacks 自身沒有以固定 B base 直接寫 B+128／B+148；它們仍會寫入動態 N 欄位，且 nested callees 未全數封閉。沒有物件非別名證據時，不可由此推論全域槽位完全不受影響。

## 重播

以 [靜態 checker](check_v4160_list_direct_callbacks_static.py) 重播：

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_list_direct_callbacks_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_list_direct_callbacks_static.py
```

本階段驗證 506 次 operand 變異拒絕、44 條選定 CFG 路徑、564 條局部 edge witnesses、65535 個正分母、byte 計數與輪替域，以及完整 JSON 一致性。CFG witnesses 僅證明編碼圖上的可走邊，沒有宣稱每個分支組合都有可達實參或 callee 正常返回。

後續重點是共用尾跳 `54c08/54cd2`、`55330/553fa`、optional `53d98/53e4a`、已定位的 outer constructors，以及實際 copy／clock provider 與完整 setup 返回後的保存條件。
