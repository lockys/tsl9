# v4.1.60 `0xa2ee` 完整分支邊界與註冊串接

2026-11-26。decoded APP 為76800 bytes，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。延續 [排程事件入口](v4160-task-event-cpu.zh-TW.md)，本批在有限 CPU 內執行完整 `0xa2ee..0xa37c` 的分支邊界、原 `0x81de`/`0x821e` getter，並接續原 `0x9124`。

所有資料與事件為離線 fixture；未知 `0xa204`、`0x10816` 及 provider 都不執行。部分 A204 返回案例使用明示假設，與自然返回分開記錄。GP fixture=`0x20004000`。本批只新增驗證腳本與說明，未改共享 CPU 或重建 C，不增加 C 覆蓋百分比；既有 C 對應 `src/native/receive/rom_dependencies.c`。

## mode 與 config5 的四種選擇

入口 frame16，依序保存 S0、RA、S1，S0保留原A0。執行原 `0x829e` 讀完整 mode byte：

- mode≠1：依序恢復S0、RA、S1/SP，以 A0=原輸入尾跳 `0x10816`。不讀config5，不寫狀態。
- mode=1：執行原 `0x81de`，得到 `V=(config5 & 3)+1`，存於S1。

| V | 原 APP 的後續行為 |
|---|---|
| 1 | A0=原輸入，呼叫 `0xa204`，RA=`0xa312`；若明示正常返回，直接返回它的完整A0 |
| 2 | 不呼叫A204，直接進readiness判斷 |
| 3 | 先呼叫A204；若明示正常返回，再進readiness，其A0被覆寫 |
| 4 | 不呼叫A204或readiness，恢復frame，自然返回A0=4 |

因此不能把 A204 的返回值一律當成「忽略」。V=1會保留它，V=3則由後續 getter 覆寫。V=1/3 的無返回假設測試只驗證到 A204入口：SP=caller−16、S0=原輸入、S1=V。

明示正常返回案例保存S0/S1、SP/GP及frame，破壞A/T暫存器。V=3後續仍需S0/原輸入；S1需保留V。V=1測試採相同較強保存前提，未聲稱已證明A204實際合約。

## 原 `0x821e(2)` 的短路與返回

readiness getter 先讀config4：bit3設定則返回0，不讀RAM狀態；否則讀 `U8[GP+195]`，完整byte小於3才返回1。

| readiness及輸入 | `0xa2ee` 結果 |
|---|---|
| readiness=0 | 自然返回0，不讀config3 |
| readiness=1、原輸入=0 | 自然返回1，不讀config3 |
| readiness=1、輸入非零、config3低nibble=15 | 自然返回1 |
| readiness=1、輸入非零、config3低nibble≠15 | 更新狀態後尾跳 `0x9124` |

A204 返回之後不重讀config5，但會重新讀config4、條件性讀GP+195/config3。6組明示hook修改這些控制欄位及counter，確認原續段使用新值；這只證明APP的讀取依賴，不代表真實A204會修改它們。

## 先更新狀態，再尾跳註冊

成功通過上述判斷時，原指令的順序為：

1. 計算 duration=`(原輸入*1000)&0xffffffff`。
2. 讀 `U8[GP+176]`，計算 `(舊byte+1)&3`。
3. 恢復caller S0，寫GP+176。
4. 恢復caller RA、S1，寫 `U8[GP+175]=1`。
5. 設 `(A0,A1,A2,A3)=(0x9f74,0,duration,0)`，恢復SP，無連結尾跳 `0x9124`。

counter不是普通byte加一：舊值3、7、255都變0。兩個stores發生在註冊函式之前，**不以註冊結果為條件**。

已將原 `0xa2ee` 的尾跳接到 [原 `0x9124` 驗證器](v4160-register-gate-cpu.zh-TW.md)，涵蓋新空槽、既有零payload、既有非零payload及全滿表。全滿表自然返回1，先前GP+175=1及counter更新仍然保留；沒有回滾。不能以這兩個欄位推論服務成功。

一般非零duration若繼續到 `[40058]`，註冊函式另做一次低32位乘1000再除625，因此該參數為 `((((輸入*1000)&MASK)*1000)&MASK)//625`；不是無限精度的兩次乘法。

**直接word探針**另確認：非零輸入 `0x20000000` 或 `0x80000000` 經第一次乘1000已溢位成0。若表有空槽，原 `0x9124` 會走duration=0快路徑，尾跳 `[40050]`；若只有既有key且無空槽，仍沿一般既有key路徑，可到 `[40058]` 或非零舊payload的未知free入口。

這些word探針不宣稱可由已知事件caller產生：原 `0x172b6` 對該參數使用config8低4位，特定mode下再限制為最大3，已知域為0..15。

## 完整事件caller的自然返回

45組實際串接從原 `0x172b6` 開始，經 disabled `0x171de` 自然早返、原post-config、完整 `0xa2ee` 及外層epilogue：

- config3低nibble=15時，A2EE自然返回1。
- config3=0/14、輸入1..15時，A2EE先更新狀態，再尾跳原9124；fixture表全滿，所以9124自然返回1。
- 外層忽略該A0，返回完整32-bit事件mask XOR1，恢復caller frame。

這45組沒有替未知callee或provider假造返回。它們證明合成狀態下的原指令控制流，不證明實機事件投遞、並行記憶體穩定或provider綁定。

## 可重跑的檢查

[test_v4160_a2ee_action_cpu.py](test_v4160_a2ee_action_cpu.py) 使用 `check()`，一般模式與 `-O` 都保留完整檢查：

```text
python analysis/test_v4160_a2ee_action_cpu.py
python -O analysis/test_v4160_a2ee_action_cpu.py
```

兩種模式輸出相同：

```text
PASS: 1280 full-mode/value cases; 12288 config5 branches; 65536 readiness-byte pairs; 768 config3/value cases; 1024 counter/word cases
PASS: 288 declared A204 returns; 6 fresh-control hooks; original A2EE-to-9124 chains {'immediate': 30, 'call': 540, 'free': 285, 'full': 285}; 45 full event/caller natural returns; 4 mutations
PASS: exact stores/read order/frame; wrapped-zero duration and pre-failure state retained; unknown callees/providers NOT executed
```

config5案例為完整256個byte × 3個輸入 × 4個RAM readiness值 × config4={0,8} × config3={0,15}；另65536組窮舉完整config4/GP+195 byte配對。counter窮舉256個舊byte並含word乘法邊界。註冊串接涵蓋每槽、輸入1..15及4個域外word探針、4種表布局，共1140組。

4個只改記憶體副本的mutation，分別將 readiness閾值3改2、counter mask3改7、pending store來源改zero、註冊key9f74改9f76；均被指定的存取/參數檢查拒絕，不以解碼失敗或unmapped access當作偵測。各段完整核對資料讀寫順序、frame、A0與尾跳參數，原BIN未修改。

原區段SHA-256（右界不含）：

| 範圍 | SHA-256 |
|---|---|
| `a2ee..a37c` | `1e3ba5cad99891ddf478123a9015736168e7bdad51c01abbed0cda7e4d043480` |
| `821e..8248` | `4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd` |
| `81de..81ee` | `fe6583f69447a91467e981387fde5e03250f7dd9c0c6a9ab25af208a5f464dc0` |

尚待驗證 `0xa204`、`0x10816` 函式體、排程key `0x9f74` 後續用途、bit1 handler `0x13d48` 及實際provider保存與payload合約。本批沒有執行未知callee、provider、IRQ或設備操作。
