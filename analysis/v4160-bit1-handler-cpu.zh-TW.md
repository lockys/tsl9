# v4.1.60 bit1 handler 與原指令狀態／計時分支

2026-11-26。76800-byte decoded APP，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批接續 [排程事件入口](v4160-task-event-cpu.zh-TW.md)，將先前僅到入口的bit1 callee `0x13d48` 展開，核對原 `0x135e6`、`0x13d48..0x13dd4` 及時鐘wrapper。

全程有限CPU、離線合成記憶體與事件，不操作設備。未知provider與TX函式體不執行；部分時鐘標量返回假設另列。既有C對應 `src/native/receive/callback_flow.c`、`callback_providers.c`；本批不修改共享CPU、原BIN或C，也不提高C覆蓋百分比。

## `0x135e6`：短路讀取，再設旗標與註冊

令R=`0x2000c794`，兩組資料位址為：

| 組別 | H（halfword） | M（byte） | A（byte） |
|---|---|---|---|
| 0 | R+2 | R+5 | R+4 |
| 1 | R+6 | R+9 | R+8 |

先讀H0；僅H0≠FFFE才讀M0，僅M0非零才讀A0。三者符合 `H0≠FFFE && M0!=0 && A0!=0` 即觸發，不讀第二組。否則同樣短路檢查第二組。M接受**任意非零byte**，FFFE才是特殊halfword，FFFF不等同它。

未觸發時不建立frame、不寫狀態，自然返回0。觸發時建frame16、保存RA，**先寫 `U8[R]=1`，再呼叫** `9124(0x1333c,0,300,0)`。RA=`0x13656`、SP=caller−16。

註冊函式正常返回後，原續段恢復RA、強制A0=1、恢復SP返回。本批以原9124全滿表自然返回1接續，因此證明：即使未新增表項，135e6仍返回1、R旗標保持1。不能以此返回值或旗標表示註冊成功。

這些資料只是位址上的讀取組合，不宣稱為獨立struct、有效實機記錄或原子快照。

## `0x13d48`：使用callee結果，再重新讀live欄位

入口frame16只保存RA，先呼叫135e6，RA=`0x13d50`。事件caller設定的入口A0=0不是後續分支判斷值；13D88測試的是135e6的返回值。

135e6返回後，caller重新讀H0：

- H0≠FFFE且M0=0：直接進13D88，不讀第二組。
- 其餘情況讀H1；H1=FFFE便早返，否則讀M1，M1非零也早返。
- 此處不讀A0/A1欄位，與135e6觸發條件不同。

早返保留135e6返回的A0，恢復RA/SP。12組明示fixture hook在callee返回後、caller續段前修改上述資料，確認續段讀到新值；hook不是provider或IRQ的實測副作用。

進13D88後：

| 135e6返回 | 原後續 |
|---|---|
| 非零 | 恢復caller frame，尾跳 `9124(0x13346,0,100,0)` |
| 零 | 呼叫原 `0x81b0`，RA=`0x13da6`、SP=caller−16 |

## 時鐘wrapper與34／35的無號差值

原81B0從 `[0x4007c]` 載入未知target。本批沿用 [時鐘wrapper驗證](v4160-timer-callback-cpu.zh-TW.md) 的標量正常返回前提：保存全部記憶體、S暫存器、SP/GP與frame，破壞A/T，再提供raw word。**未執行該target**。

原wrapper計算 `now=((raw*10)&0xffffffff)>>4`，因此其實際輸出域為0..0fffffff。續段讀 `U32[GP+344]`，算 `delta=(now-stamp)&0xffffffff`：

| 無號delta | 行為 |
|---|---|
| ≤34 | 讀saved RA，恢復SP，尾跳 `9124(0x13346,0,35,0)`；不改stamp |
| >34 | **先讀saved RA，再store GP+344=now**，設A0=0、恢復SP，尾跳 `0x13346` |

stamp>now造成的32-bit wrap也使用上述無號比較。1554組條件性時鐘案例包括delta=0..255及7fffffff、80000000、ffffffff，raw取6種word邊界；stamp由fixture明示設定，不宣稱所有初始stamp均能由實機歷史產生。

數字34、35、100、300的單位未證明。到達13346只是APP傳輸建構函式的入口，不能當作已送出資料或傳輸完成。

## 接回真正bit1事件caller

本批實際執行 `172b6 → 13d48 → 135e6 → 13d48 → 1731a → caller`，取代先前bit1返回假設的部分路徑：

- 16384組完整16-bit「bit1設置、bit0清除」mask，及2組高位word，使用兩個H皆FFFE的合成狀態；callee自然早返，原caller返回完整32-bit mask XOR2。
- 另2組由135e6觸發、原9124全滿自然返回、再尾跳原9124(duration100)全滿自然返回，最後回到事件caller；R旗標仍為1。

合計16388組caller鏈沒有未知返回假設，不代表所有handler分支均已自然返回。時鐘及TX分支分別保留明示時鐘前提與TX入口邊界；真實事件投遞及並行時序仍未證。

## 驗證

[test_v4160_bit1_handler_cpu.py](test_v4160_bit1_handler_cpu.py) 使用 `check()`；一般模式與 `-O` 的檢查相同：

```text
python analysis/test_v4160_bit1_handler_cpu.py
python -O analysis/test_v4160_bit1_handler_cpu.py
```

輸出：

```text
PASS: 131072 halfword sentinel probes; 1536 mode/action bytes; 729 original branch combinations {'return': 441, 'clock': 192, 'schedule100': 96}; 12 fresh-state hooks
PASS: 1554 declared-clock elapsed cases {'schedule35': 210, 'tx': 1344}; 16388 actual bit1 event/callee returns; 4 mutations
PASS: exact read/store/frame and pre-failure flag; clock premise explicit; TX/provider bodies NOT executed
```

131072探針分別窮舉兩個H的完整65536值；觸發分支停在原9124入口，不執行provider。1536組另測每組M的全部byte與A={0,1,255}，並沿原全滿註冊自然返回。729組是六欄位各3種值的笛卡兒積，分別停在返回、時鐘或註冊入口；不是729組完整TX。

四個記憶體副本mutation：第一組sentinel常數FFFE改FFFF、R旗標store來源改zero、delta閾值34改35、duration100改101。均由指定的存取／參數檢查拒絕，不以解碼或unmapped錯誤當作偵測。各段完整核對資料讀取順序、stores、frame及尾跳參數，原BIN未修改。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `135e6..13660` | `7b7aaecef25f693b79f672a0e687b6a624c22e9588005652089e6528c612b90a` |
| `13d48..13dd4` | `32ef96a7aaa9a7a8d64bc93b5589b3dda7713a3b4d6cb4cb8129a9e02e4d1d23` |
| `81b0..81ca` | `f03a9478d6361df881745068e9c322098ea7317e3bb4d1be5f62f97ff7e4c239` |

後續仍需串接13346的既有TX建構驗證、釐清R/GP+344等狀態來源與真正provider綁定，以及保存／payload生命週期。本批沒有執行未知provider、TX函式體、IRQ或設備操作。
