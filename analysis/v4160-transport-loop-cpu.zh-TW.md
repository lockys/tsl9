# v4.1.60 TX stack 至 transport admission 與兩筆記錄返回

2026-11-26。原decoded APP：76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。接續 [TX fields38..43](v4160-tx-fields-cpu.zh-TW.md)，本批沿同一有限CPU與真實stack指標，串接原8A56 admission、frame/checksum、POST尾跳及135AC記錄迴圈。

全部離線合成狀態。copy/fill、時鐘、lookup及POST正常返回／保存條件均為明示前提，不執行任何provider、設備或實際posting。既有C及 [transport frame驗證](v4160-transport-frame-cpu.zh-TW.md) 已描述單獨入口；本批補TX caller的同一stack來源與跨記錄控制流，不把舊成果當新C覆蓋，未改共享CPU或原BIN。

## 從原lookup入口判斷admission

前批原8A56已建立32-byte nested frame，到達primary lookup：A0=handle、A1=GP+128、RA=8a90。此時S0=76、S1=TX frame F+20、S2=handle、S3=command160。

本批明示lookup正常返回，保存S暫存器、GP/SP、TX及nested frame與所有記憶體，破壞A/T並提供完整A0：

- **完整word恰等於1**才admit bank0。2、256、257、0x80000001、0xffffffff等非零值不成立，不能只看低byte或bit。
- primary未admit後，原碼重新讀 `U16[GP+154]`；匹配且非FFFE才呼叫secondary lookup，RA=8ab6，參數仍為(handle,GP+128)。
- secondary完整reply=1才admit bank1；否則自然恢復RA/S0/S1/S2/S3/SP，返回最後lookup的A0。若未進secondary，保留primary reply。

4160組皆從已實際進入primary lookup的TX鏈開始，不宣稱窮舉所有handle或所有8A56入口狀態。另4組明示primary返回後修改secondary handle，確認後續重新讀取；這是fixture變更，不是實測provider副作用。

## 原APP逐byte讀TX stack，寫frame與checksum

admit後選buffer=`0x2000b18c + 1062*bank`，來源是原caller的 **F+20..F+95，長度76**。原8A56執行LBU/SB迴圈，沒有經過copy provider。

| buffer位置 | 寫入 |
|---|---|
| +6..10 | `[55,7f,a0,00,4c]`（十六進位） |
| +11..86 | 76個TX stack bytes，按序讀一個、寫一個 |
| +87 | `(160+76+sum(payload)) & 255` |
| +2 halfword | 82 |
| +4 halfword | 0 |

精確順序是marker SH、length low、length high、command、逐byte payload、checksum；再讀saved RA/S1/S2/S3，寫metadata，讀saved S0，最後讀40050與task byte。兩個完整resident buffer都與獨立預期比對，未修改bank及區域保持舊值。

以上是原APP在合成狀態下的frame布局，不證明實機資料、實際送出或通訊成功。

## POST入口與明示返回

原8B50尾跳 `[40050]` 時，transport frame已恢復：RA=135ac、SP=F，S0=40000、S1=當次記錄指標、S2=index、S3=FFFE。參數：

```text
A0 = U8[GP+148+4*bank]
A1 = 1
A2 = GP+148+4*bank
```

512組覆蓋全部256個task byte與兩個bank。服務本體不執行；需要接回135AC時，測試另明示POST正常返回，保存TX仍live的S暫存器、GP/SP/frame及全部記憶體，破壞A/T並提供完整reply。這不是provider保存或事件投遞的證明。

拒絕路徑可由原transport自然返回；admit路徑只有在上述POST前提下才接續caller，兩者在報告與測試中分開。

## 135AC重新讀第二筆記錄

S2=0時，原迴圈設S2=1、S1=4，重新讀第二筆H/M/A：

1. H=FFFE不讀M/A。
2. H有效、M非零不讀A。
3. H有效、M=0才讀A，**先寫F+23=1**，A非零進原FA2A、A=0進135CA。

跳過第二筆時不改F+23；162組fixture在transport返回後改第二筆欄位及stack byte，確認使用新值與短路順序。不是入口snapshot，也不沿用第一筆的絕對記錄指標。

S2=1時，原碼恢復TX saved RA、S0..S7、SP+=144直接RET；A0沒有重新設定成功碼，保留transport拒絕值或明示POST返回值。

## 兩筆共用frame的欄位保留

第一筆走有效A非零組裝，第二筆走A=0清除路徑時，原碼只清F+38..39及請求指定區域fill，**不重寫F+40..43**。因此會保留第一筆的時間halfword、mode/flag byte與readiness byte。

16組完整鏈驗證此結果。當前fixture採raw=FFFFFFFF、mode=31、GP356=1、三個readiness均1，F+40..43的little-endian word為 `0x079f0031`；這是該fixture的具體結果，不是固定格式常數。它說明同一stack frame的跨記錄資料流，不賦予欄位物理用途。

第二筆admit bank1時，另核對bank0保持先前內容；此結果仍以POST保存記憶體的前提為限。

## 完整兩筆與事件caller鏈

96組涵蓋：第一筆A非零／A=0；第二筆有效／A=0／跳過；兩次admission接受／拒絕；POST reply=0／FFFFFFFF；直接TX入口或真正bit1 caller入口。

其中事件版本實際執行：

```text
172b6 → 13d48 → 135e6 → clock wrapper → 13346
      → 原資料建構/getters → 8a56 → lookup → POST邊界
      → 明示返回 → 原第二筆 → 原TX epilogue → 1731a → caller
```

所有APP控制流與資料stores均執行原指令；未知時鐘／資料／lookup／POST返回仍保留前提，不因此宣稱實機整鏈、完整啟動、非同步IRQ或真正傳輸已證明。

## 驗證

[test_v4160_transport_loop_cpu.py](test_v4160_transport_loop_cpu.py) 使用 `check()`；一般與 `-O` 結果一致：

```text
python analysis/test_v4160_transport_loop_cpu.py
python -O analysis/test_v4160_transport_loop_cpu.py
```

```text
PASS: chained admission cases {'return': 3626, 'bank0': 16, 'bank1': 518}; 512 task bytes/banks; 4 fresh secondary probes; 162 next-record live-state cases
PASS: 96 complete two-record/event chains; 16 observed fields40..43 carry-over cases; 4 mutations
PASS: original 76-byte stack payload/frame/checksum; lookup and POST returns explicit; no provider/posting/device execution
```

admission矩陣為primary reply={全部256個byte、256、257、0x80000001、0xffffffff} × secondary reply={0,1,2,0xffffffff} × secondary匹配／不匹配 × 兩個記錄位置。所有案例完整核對資料讀取、stores、返回／尾跳暫存器、原TX frame與兩個resident buffers。

四個記憶體副本mutation：primary admission值1改2、marker常數改值、payload store偏移5改7、下一筆index1改0。最後一組回讀第一筆並由指定存取檢查拒絕；不使用越界index造成的unmapped失敗當作偵測。原BIN未修改。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `8a56..8b6e` | `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b` |
| `135ac..135ca` | `2ea43e8f88b18a5ef24dfad15b3cb9a5172cd7773de3c42a570002066c0f2c41` |

後續需釐清installed provider的靜態綁定、真實資料來源與保存／payload合約，及其他尚未展開的APP呼叫。這批完成的是明示前提下的transport／兩筆迴圈串接，未執行provider、posting或設備操作。
