# v4.1.60 bit1 至 `0x13346` 建構入口的原指令驗證

2026-11-26。decoded APP：76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。接續 [bit1 handler](v4160-bit1-handler-cpu.zh-TW.md)，將其直接TX尾跳接到原 `0x13346` 建構入口與 `0x9e84`、`0x92ba`、`0xd1a8` 本機包裝函式。

既有 [13346靜態組裝說明](13346-pack-window-bounded.zh-TW.md) 與 `src/native/receive/callback_flow.c` 已記錄該函式。本批補原指令執行、精確frame及服務邊界驗證；不把舊C當作新成果，未重建C、未改共享CPU或提升C覆蓋百分比。

所有記憶體、來源bytes與provider指標皆為離線fixture。以下copy/fill返回效果是**明示假設**，不是執行provider或讀取真實ROM/RAM。沒有設備、實際傳輸或IRQ操作。

## 144-byte frame與首個8-byte來源

令入口SP為P，TX frame基址F=P−144。保存順序為RA、S0、S2、S3、S4、S5、S6、S7，最後S1；之後實際呼叫 `0x9e84`，RA=`0x13362`。

9E84先讀 `[4004c]`，建32-byte nested frame，向未知target傳入 `(F−32,0x08077b00,8)`，RA=`0x9e9c`。本批在入口停止，再明示寫入8個合成bytes及正常返回。原續段從stack讀兩個完整words至A0/A1；provider返回的標量A0不被當作這兩個資料words。

回到13362後，**先讀 `[40048]`**，才依序將資料拆成halfwords：

| store位置 | 值 |
|---|---|
| F+12 | low16(word0) |
| F+16 | low16(word1) |
| F+14 | high16(word0) |
| F+18 | high16(word1) |

接著到fill邊界 `(F+20,0,76)`，RA=`0x13382`。APP自己沒有清這76 bytes；測試分別採「明示填零」與「完全不填、僅返回」兩種前提。

## buffer前3 bytes與兩段資料copy

fill返回後，APP寫buffer前三bytes `[0, F[12], F[13]]`，再呼叫原92BA，輸入dst=F+24。

| 邊界 | 參數 | RA／SP |
|---|---|---|
| 92BA第一段 | `(F+24,0x1ffff7ec,8)` | RA=92d8，SP=F−16 |
| 92BA第二段 | `(F+32,0x1ffff7e8,6)` | RA=133a6，SP=F，frame已恢復 |

第一段返回後，92BA仍需要live S0=`1ffff000`、S1=`40000`、S2=原dst；它**重新讀 `[4004c]`**，恢復S0/RA/S1/S2/SP後尾跳第二段。兩個來源是原指令的地址參數，不據此認定真實資料內容或晶片識別語意。

外層133A6再讀 `[4004c]` 至S0，才呼叫原 `0xd1a8`。該getter只返回 `0x2000bf48`，沒有讀取19 bytes。之後第三個copy邊界為 `(F+60,0x2000bf48,19)`，RA=`0x133b4`、SP=F。

## 重新讀slot與先捕獲target並不相同

測試明示替換合成slot指標，核對兩種行為：

- 92BA第一段返回後會重新讀4004C，第二段使用新target。
- 外層133A6也重新讀4004C，並存入S0。
- 在S0載入後、D1A8執行前再次改slot，第三copy仍使用**先前捕獲的S0 target**。

這證明APP的載入時機，不證明installed provider身分、指標實際會變化或真實服務合約。

每個正常返回hook保存S暫存器、GP/SP及saved frame，僅依明示前提寫指定目的範圍，並破壞A/T暫存器。SID與分段資料等名稱只作fixture標籤，不代表已取得實機來源。

## 兩筆記錄跳過時的條件性返回

對每筆記錄，原迴圈先讀halfword H；H=FFFE即跳過，不讀M。否則讀mode byte M，非零亦跳過；M=0的active-record建構路徑不在本批展開。

若兩筆皆跳過，原迴圈恢復RA、S0..S7與SP直接RET，不呼叫傳輸callee。**這條路徑不設定成功碼**，A0保留最後19-byte copy返回的完整word。本批用0及FFFFFFFF兩種reply核對，不能將其視為傳輸結果。

6144組完整prefix/skip案例核對整個144-byte frame：明示copy/fill的bytes、原APP stores與saved registers皆比對，未修改區域保持入口snapshot。`zero_fill=False`時未寫洞位保持舊stack內容，沒有偷偷把整個buffer補零。

這是未知服務按明示前提返回時的APP結果，不是完整13346行為或設備執行證據。

## 真正bit1 caller接到第三copy入口

24組從原 `0x172b6` 的bit1分支開始，依序執行13D48、135E6、原時鐘wrapper、timestamp更新、13D48恢復frame並尾跳13346，再跑上述入口：

```text
172b6 → 13d48 → 135e6 → 13d48 → 81b0
       → 13d48 → 13346 → 9e84 → fill → 92ba → d1a8 → 19-byte copy入口
```

時鐘只採先前的raw標量返回前提；其後資料與fill亦使用上述明示效果。delta選35、36、80000000、FFFFFFFF，raw採0、16、FFFFFFFF，並分別測固定／替換copy指標。

這24組只到第三copy入口，不把服務當作已返回，也不跳過active-record後段去宣稱完整TX。實際送出、資料內容、provider保存與事件投遞仍未證。

## 可重跑的檢查

[test_v4160_tx13346_prefix_cpu.py](test_v4160_tx13346_prefix_cpu.py) 使用 `check()`；一般及 `-O` 模式結果相同：

```text
python analysis/test_v4160_tx13346_prefix_cpu.py
python -O analysis/test_v4160_tx13346_prefix_cpu.py
```

```text
PASS: 6144 original TX prefix/skipped-record returns; 49 skip predicates; 24 bit1-to-TX local-copy boundaries; 4 mutations
PASS: exact frame/halfword/copy arguments; slot rereads AND captured target; fill and data-return premises explicit
PASS: ROM/RAM sources not read; provider bodies, transport and device operations NOT executed
```

6144組為256種低bytes樣式 × 3種word高halfword × fill有／無 × slot固定／替換 × reply={0,全1}；第一word兩個低bytes使用 `low` 與 `low XOR A5`，不是全部65536種低halfword配對。另49組窮舉指定H={0,FFFE,FFFF}、M={0,1,255}中兩筆皆可跳過的組合。

四個記憶體副本mutation：fill長度76改77、第二copy長度6改7、第三copy長度19改18、getter來源指標BF48改BF4A。均由指定參數或getter結果檢查拒絕，不將解碼／unmapped錯誤當作偵測。原BIN未修改；實際ROM/RAM來源未映射讀取，也未執行provider。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `13346..133b4` | `030c400f491fea721a75fee84f55628d4386169a7f8ea1f17c005917a30f3a86` |
| `9e84..9ea6` | `a82d722d2d9a4e4ce5ef4860545790074e01a36f5b6696859d3615ea3b3373d6` |
| `92ba..92f2` | `c68e81ca8b76f4b7ccec0329967a2c991fedd9115392b899c79301ff86f5ccb6` |
| `d1a8..d1b2` | `ef3cbb3bbf73c68e553e53c42f8a0b40a95e5d3547b09f25e4fb42ebf80fb7e5` |
| `135ac..135ca` | `2ea43e8f88b18a5ef24dfad15b3cb9a5172cd7773de3c42a570002066c0f2c41` |

後續仍需展開active-record的資料組裝／getter鏈，接到既有8A56傳輸入口驗證，並釐清真實資料來源、provider綁定與保存／payload合約。本批未操作設備、IRQ或實際傳輸。
