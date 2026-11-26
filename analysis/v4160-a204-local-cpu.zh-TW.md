# v4.1.60 `0xa204` 本機狀態流程與 `0x10816` 尾跳

2026-11-26。原 decoded APP：76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。延續 [A2EE完整分支驗證](v4160-a2ee-action-cpu.zh-TW.md)，本批在有限 CPU 內執行 `0xa204..0xa2ea`、原 `0xb6ea`、`0x10816..0x1083c`，並串接原 caller/註冊函式。

全程使用離線合成狀態，不操作設備。未知APP callee `0xd05c` 與未知取樣provider均停在入口；取樣的明示返回案例另列。欄位名稱僅用於描述程式資料流，沒有賦予實體按鍵、燈號或時間單位的語意。

本批未修改共享執行器、原BIN或C；已有C對應 `src/native/receive/rom_dependencies.c`、`state_output_dependencies.c`，不新增C覆蓋百分比。GP fixture=`0x20004000`。

## GP+172 優先於其他欄位

`0xa204` 建frame16，只保存RA。S暫存器本體沒有使用或修改。

| GP+172與輸入 | 行為 |
|---|---|
| GP+172非零、輸入0 | 自然返回A0=0 |
| GP+172非零、輸入非零 | 執行原8202讀 `U8[0x2000bee1]` |
| 上述getter=0 | 自然返回0 |
| 上述getter非零 | 恢復RA/SP，尾跳 `0xd05c(3,1,0)`；不當作已返回 |

此分支完全跳過GP+179及config讀取。GP+172為0時，才進入下面的byte狀態流程。

## GP+179 的完整byte與輸入低byte

- 輸入非零、GP+179非零：沒有狀態stores，返回**原完整32-bit輸入**。
- 輸入非零、GP+179=0：先寫 `GP+179=low8(輸入)`，再進config分支。即使輸入=`0x100`、實際存入0，也繼續處理；完整輸入非零判斷與byte儲存不能合併。
- 輸入0、GP+179=0：返回0。
- 輸入0、GP+179非零：寫入減1後的byte。仍非零則返回0；恰減至0時，讀GP+178並寫 `int(舊值==0)`，再進輸出選擇。這條路徑不讀config。

## 新非零輸入的 config 更新

先讀config4，依其高2位更新GP+180：

| `config4 >> 6` | 寫入GP+180 |
|---|---|
| 0 | 0 |
| 1 | 1 |
| 2 | `int(舊GP+180==0)`，額外讀舊byte |
| 3 | 3 |

接著使用**同一個config指標**讀config9低2位：0寫GP+178=0；1寫1；2保持舊byte；3讀 `[0x40038]` 並呼叫未知target。

取樣入口RA=`0xa2a0`、SP=caller−16、A0仍是原完整輸入。此時GP+179及GP+180已更新，但GP+178尚未依取樣結果更新。無明示返回值時，腳本在此停止並核對先前stores，沒有直接略過未知服務。

9216組明示取樣返回測試保留所有記憶體、S暫存器、SP/GP及saved frame，破壞A/T暫存器，提供完整word返回值。原續段執行 `A0&=1`、寫GP+178，再重新讀GP+180及條件性GP+174/GP+178。這是保存前提下的APP結果，未證明provider實際返回或其保存合約。

## 輸出選擇與原 `0xb6ea` 自然返回

共同續段先讀GP+180：

| 條件 | 行為／A0 |
|---|---|
| GP+180=0，GP+174非零 | 自然早返，保留目前A0；一般為原輸入，取樣後則為低bit |
| GP+180=0，GP+174=0 | 讀GP+178；非零選3，零選1 |
| GP+180=3 | 讀GP+178；非零選10，零選12 |
| GP+180其他非零 | 讀GP+178；非零選11，零選9 |

選出代碼的路徑先恢復RA/SP，再尾跳 `0xb6ea`。本批直接執行該原始10-byte leaf：把A0低byte寫到 `0x2000bf0c`，RET，A0完整值保持。沒有替它假造返回。

因此160組 `0xa2ee → 0xa204 → caller` 可以完整執行原指令自然返回：V=1保留實際local返回A0；V=3再經原readiness getter，由fixture的config4 bit3阻擋而返回0。到達D05C的分支不被算入自然返回。

## `0x10816`：零輸入先轉1，再註冊

mode≠1 的原A2EE尾跳到此函式。它沒有建立frame：

1. 原輸入0則先改為1，其他完整word保持。
2. 計算duration=`(調整後輸入*1000)&0xffffffff`。
3. 寫 `U8[0x2000bfb8]=1`。
4. 以 `(A0,A1,A2,A3)=(0x1061c,0,duration,0)` 尾跳原 `0x9124`，保持原RA/SP及S暫存器。

420組實際 `A2EE → 10816 → 9124` 串接涵蓋每槽、4種表布局、輸入 `{0,1,15,256,0x20000000,0x80000000,0xffffffff}`。兩個非零word溢位成duration0，可進立即服務尾跳；原輸入0則先正規化1，duration=1000。

表全滿時原9124自然返回失敗，先前BFB8旗標仍為1，沒有回滾。非零舊payload與排程provider分支均停在服務入口。已知事件caller對輸入使用0..15；域外word僅為直接入口算術探針，不宣稱實機可達。

## 驗證

[test_v4160_a204_local_cpu.py](test_v4160_a204_local_cpu.py) 使用 `check()`，不受 `-O` 移除：

```text
python analysis/test_v4160_a204_local_cpu.py
python -O analysis/test_v4160_a204_local_cpu.py
```

兩種模式輸出相同：

```text
PASS: 65536 config4/config9 pairs; 3072 flag/input/ready gates; 1024 latch/input cases; 3072 retained-state releases; 9216 declared sample returns; 256 ready bytes
PASS: A2EE-to-10816-to-9124 chains {'immediate': 30, 'call': 180, 'free': 105, 'full': 105}; 160 original A2EE/A204 parent returns; 4 mutations
PASS: exact accesses/stores/frame; input low-byte latch and zero normalization; D05C and sample target NOT executed
```

65536個config配對窮舉完整config4/config9 bytes，**包含停在取樣入口的案例**，不全是自然返回。GP+179與四種輸入、GP+178與保留狀態、GP+172優先路徑及getter完整byte均另測；取樣標量探針採 `{0,1,2,全1}`。每段完整核對存取順序、stores、frame、A0及鄰接canary。

四個只改記憶體副本的mutation：GP+179的SB來源改zero、取樣低bit mask1改3、零輸入正規化1改2、註冊key1061c改1061e。均由指定的存取／參數檢查拒絕，未將解碼或unmapped錯誤當作偵測。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `a204..a2ea` | `4d6358bb163043666ddbcae3d8e15d10f9408f914d9b66950bae496db86157a7` |
| `b6ea..b6f4` | `8fcc628137490440fc900f4b192ecd4a08b58744a91ecdd5effd46e3592479e9` |
| `10816..1083c` | `ae741295c7fd3965b402bda90d7592f13ae0bc7eb5e32bda935eeb222f5388b7` |

後續待展開APP callee `0xd05c`、已定位的callback `0x1061c`/`0x9f74`、bit1 handler `0x13d48`，以及實際provider綁定與保存／payload合約。本批未執行未知callee、provider、IRQ或設備操作。
