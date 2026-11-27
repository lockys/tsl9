# v4.1.60：外層物件配置、函式發布與清除尾段

本階段將上一輪定位的兩個 outer-slot writers、兩個 constructor 位址 publisher，以及 `55330/553fa` 尾段，轉成完整原始指令與 CFG 證據。新增 **976 bytes／308 條指令**，重播 22 條選定路徑；既有 C 重建覆蓋率沒有改變。

全程只讀取原始 APP、SDK、兩份 resident 參考候選與本機指令參考，產生分析檔案。沒有執行或模擬目標 ISA、allocator、fill、callback、provider、MMIO 或裝置；候選對應不代表原裝置已安裝此 resident。

| 完整本體 | V1.31 範圍，不含尾端 | V1.40 範圍，不含尾端 | 每版 bytes／指令數 |
|---|---|---|---|
| B+128 constructor | `5e8bc..5e950` | `5e9a6..5ea3a` | 148／48 |
| B+148 constructor | `57cbe..57d58` | `57dfe..57e98` | 154／47 |
| 清除尾段 | `55330..55384` | `553fa..5544e` | 84／30 |
| B+132 publisher | `60856..6089a` | `60940..60984` | 68／20 |
| B+152 publisher | `58ef2..58f14` | `5903a..5905c` | 34／9 |

各本體 SHA-256、逐條欄位、stores、calls 與路徑見 [機器可讀證據](v4160-list-outer-objects-static.json)。沒有將已驗證的 34-byte caller、22-byte registrar、48-byte task registrar、258-byte handler 或先前直接 callbacks 再算成新增 bytes。

## 三種槽位與兩層 callbacks

B=`200033b8/20003408`。沿用 [handler 證據](v4160-list-setup-handler-static.zh-TW.md)，巢狀事件先載入 B+128／B+148 的物件指標，再讀物件內的 function word；只有後者有本機 null guard。outer pointer 本身仍需要有效物件與存活期前提。

| 用途 | B 相對位置 | 這次接通的內容 |
|---|---|---|
| 已配置的 outer object | +128、+148 | constructors 成功路徑發布的 N |
| constructor 函式位址 | +132、+152 | publishers 寫入 `5e8bc/5e9a6`、`57cbe/57dfe` |
| 供 registrar 使用的另一組 callback 來源 | +320、+312 | publishers 寫入 `60516/60600`、`58c52/58d9a` |

後兩列的函式位址發布，都不等同已呼叫 constructor 或已建立 outer object。registrar 的 callback 也不同於 handler 從 outer object 取出的巢狀 callback，不能混成同一層綁定。

## 配置與發布順序

兩個 constructors 都使用 16-byte frame，保存 RA、S0。先請求 RAM `20000040`，把回覆保存成 S0=N。回覆為零時直接進入共同返回處，本機跳過 fill、outer-slot 與物件欄位寫入，最後返回 0。

這表示失敗分支**沒有本機清除舊槽位**。若要進一步聲稱舊值完全保存，仍需 allocator 與其他 writers 未改動該值的前提。

| constructor | allocation 請求 A0、A1 | fill 請求 | 發布位置 | explicit 物件存取所需範圍 |
|---|---|---|---|---|
| B+128 | 232、622 | `2000039c(N,0,232)` | `U32[B+128]=N` | 至少 130 bytes |
| B+148 | 160、585 | `2000039c(N,0,160)` | `U32[B+148]=N` | 至少 156 bytes |

成功路徑共同順序是 allocation → fill 返回 → **發布 outer pointer** → explicit defaults／來源 word／function words → optional registrar → 返回原 N。fill 的實際 provider、有效範圍、正常返回及 S0／SP／frame 保存仍需證明；非零回覆本身不保證可讀寫或存活。

outer pointer 的發布早於所有 explicit 物件欄位寫入。因此本機原指令不提供「完整物件一次發布」的保證；是否存在並行觀察、何時進入 handler，以及欄位在讀取時是否已完成，均未證明。

## 物件欄位與 handler 串接

| outer object | 直接 defaults | 兩個來源 word | function words，V1.31／V1.40 |
|---|---|---|---|
| B+128 的 N | N+8=0、N+10=0、halfword N+48=`ffff`、N+125／129=`ff` | fresh `20003534/20003584` → N+116；fresh `20003538/20003588` → N+120 | N+104=`5e76c/5e856`；N+108=`604a6/60590`；N+112=`60350/6043a` |
| B+148 的 N | N+4=0、N+6=`b1`、N+64=`ff` | 同兩個來源 → N+148／152 | N+136=`57b7c/57cbc`；N+140=`58036/58176`；N+144=`57eea/5802a` |

每組來源都是兩次獨立 word loads，兩個 loads 都在兩個對應 stores 之前；沒有把它們當成原子快照。

conditional handler targets 因此接通為：

| 事件 | outer-slot | 物件 function offset | conditional target，V1.31／V1.40 |
|---|---|---|---|
| bit2 | B+128 | +108 | `604a6/60590` |
| bit3 | B+128 | +112 | `60350/6043a` |
| bit4 | B+148 | +140 | `58036/58176` |
| bit5 | B+148 | +144 | `57eea/5802a` |

232／160-byte 請求分別涵蓋 handler 需要的 116／148-byte 欄位範圍。這只是請求大小與本機存取相容；並未證明實際 allocation extent、保留期限或原裝置綁定。

## Optional registrar 與發布來源

兩個 constructors 在 fresh byte `20003240/20003290` 為零時，才呼叫已驗證的 `43b28/43bb4`。其完整 22-byte 本體沿用 [來源／registrar 證據](v4160-loaded-hook-sources-static.zh-TW.md)：unsigned A1<=4 時寫入一個 table word，沒有其他 call，也不執行傳入的 callback。

| constructor | A0 來源 | A1 | registrar 寫入位置，V1.31／V1.40 |
|---|---|---|---|
| B+128 | fresh `U32[B+320]` | 3 | `200031d4/20003224` |
| B+148 | fresh `U32[B+312]` | 4 | `200031d8/20003228` |

這些目的 word 與兩個固定 outer slots 不重疊。matching registrar 本身也不寫 S0、SP、RA 或 A0。若 N 與全域槽位／table／frame 不重疊、allocation／fill 保持必要狀態，且沒有其他干擾，則可將已發布的 N 與 function literals 保存到 constructor 正常返回之後。這個條件性結論仍不提供物件之後的存活期。

兩個 publishers 則補上 A0 來源候選：B+132 publisher 寫 B+320=`60516/60600`；B+152 publisher 寫 B+312=`58c52/58d9a`。只有 publisher 先執行、來源未被替換時，才可把這些值帶入上述 registrar 寫入結果。

既有完整 caller `5a004/5a14c` 依序呼叫這兩個 publishers，再發布自身的另一個來源 word。本階段重新核對其原始 bytes 與兩個新本體的直接呼叫目標，沒有將 caller 重複計入新增覆蓋。

B+132 publisher 另有 fresh gate `2000319f/200031ef`：非零時跳過 setup；零時先登記 handler `5352c/535da`，再把**原 registration 回覆，包括 255**傳入 `5362e/536dc`，沒有先檢查失敗碼。只有這條 setup 呼叫正常返回，才會到後面的函式位址發布。先前 task registrar／完整 setup 的證據與未封閉邊界繼續有效。

## `55330/553fa`：清除欄位，尚非已證明釋放

沿用 [直接 callback 證據](v4160-list-direct-callbacks-static.zh-TW.md)，bit0 的其中一條尾跳會以原 N 進入此完整本體。它沒有 N null guard，frame16 保存 RA、S0、S1；本機 explicit 存取需要至少 23 bytes，其他 callees 的範圍未知。

順序為：

1. 呼叫 `63e58/63f42(N)`；正常返回後把 A0 再設為原 N。
2. 依序將 N+12、N+11、N+9 三個 byte 清零，再呼叫 `53d98/53e4a(N)`。
3. 呼叫 `439a8/43a34(fresh gate byte,1)`；**重新讀取** gate byte，再呼叫相同服務 `(fresh gate byte,2)`。
4. 讀 fresh `U8[N+22]`。恰為 255 時跳過最後服務與 store，本機返回 A0=255；其他 255 個 byte 值先呼叫 `43a14/43aa0(讀值)`，返回後將 N+22 設為 `ff`，並保留該服務的 A0 作本機回覆。

沒有本機固定 head／tail／count／B+88／B+100 槽位清除，也沒有 explicit unlink 或已證明 free。動態 N stores 的全域別名、callee 是否替換或釋放 N、清零欄位是否被後續 callee 改寫，都未封閉。尤其 N+12 本機清零不能直接保證下一個 bit1 事件能安全使用 B+100。

## 驗證與後續邊界

[靜態 checker](check_v4160_list_outer_objects_static.py) 對全部 308 條新增指令做指定 operand 變異拒絕，核對 22 條局部 CFG 路徑、256 個 N+22 byte cases、固定 registrar indices、物件 store intervals，以及完整 ledger 一致性。局部 CFG 無循環，不等同未知 callees 或 setup 必然返回。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_list_outer_objects_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_list_outer_objects_static.py
```

另一個共用尾跳 `54c08/54cd2` 已定位為每版 1,220-byte 的完整大函式，包含 polling 與多個 pointed-object／copy 操作；它沒有納入本次 976-byte 證據或正常返回結論。後續需獨立展開其控制流、constructor function-slot 的真正消費者、巢狀 callback 本體，以及實際 allocator／fill 綁定與物件保存期。未宣稱所有 writers 或實際事件排程已封閉。
