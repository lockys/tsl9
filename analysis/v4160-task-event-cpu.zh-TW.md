# v4.1.60 排程事件入口、狀態旗標與原指令返回

2026-11-26。76800-byte decoded APP，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批以有限 RV32IMC 執行器核對 `0x172b6` 事件入口、原 `0x171de` 的可達早返、`0xa2ee` 的一條自然返回，以及 `0x9fb2 → 0x17320`。僅使用離線合成記憶體與事件輸入，不執行未知 provider 或操作設備。

延續 [171de 算術與 gate](v4160-schedule-171de-cpu.zh-TW.md)、[callback 狀態寫入](v4160-callback-dispatch-cpu.zh-TW.md) 與 [callback 註冊入口](v4160-callback-lifecycle-cpu.zh-TW.md)。GP fixture=`0x20004000`。本批未改共享執行器或重建 C；既有 C 對應 `src/native/receive/rom_driver_family.c`、`rom_dependencies.c`、`state_action_support.c`，不增加 C 覆蓋百分比。

## `0x172b6` 的兩個事件分支

入口 frame16，保存順序為 S1、RA、S0，S1 保留完整輸入 A1 mask。

| mask 條件 | 原指令行為 |
|---|---|
| bit0=1 | 優先呼叫 `0x171de`，RA=`0x172ca`；bit1 不在本次執行 |
| bit0=0、bit1=1 | A0=0，呼叫 `0x13d48`，RA=`0x1731a` |
| bit0/bit1 都為0 | 不呼叫，恢復 frame 返回 A0=0 |

bit0 後續 handler 正常返回時，原 `0x17300` 計算 `A0=S1 ^ 1`；bit1 handler 正常返回時，原 `0x1731a` 計算 `A0=S1 ^ 2`。**沒有截斷16位**：例如 bit1 的明示正常返回測試，mask=`0x80000002` 最終為 `0x80000000`。若根本沒有 bit0/bit1，則直接返回0，不能套用相同剩餘 mask 公式。

這與 [表消費者 `0x901a`](v4160-callback-dispatch-cpu.zh-TW.md) 不同：後者掃描低15位，並把剩餘 mask 截成16位。兩個入口不能共享同一個簡化返回模型。

## 原 `0x171de` 返回後重新讀 config

在 `0x171de` 的已知早返路徑後，原 caller `0x172ca` 依序讀 config 指標、config+8、config+3，先取 `S0=config8 & 15`。

只有 `config3 & 15 == 15` 才執行原 `0x829e` getter 讀取 `U8[0x2000bfb5]`。getter **完整 byte 恰等於1** 才把 S0 限制為 `min(S0,3)`；mode=2、255 等其他非零值不限制。然後以 A0=S0 呼叫 `0xa2ee`，RA=`0x17300`，SP=caller−16、S1=原 mask。

若排程 gate 未早返，測試沿原 `0x171de` 執行至 `[0x40038]` 的取樣入口即停止；這條路徑不被當作已返回，也不直接跳過取樣/排程服務去跑 caller 後續。

## `0xa2ee` 的自然返回子路徑

本批只在 **mode=1 且 config5低2位=3** 的條件下展開該函式：

1. 再建 frame16，保存 S0、RA、S1，S0=輸入參數。
2. 執行原 `0x829e`，得到 mode=1。
3. 執行原 `0x81de`，讀 config5，結果 `(config5 & 3)+1=4`。
4. 4 的 bit0/bit1 都為0，不呼叫 `0xa204` 或 readiness getter；直接經 `0xa372..0xa37c` 恢復 frame，返回 A0=4。
5. 外層原 `0x17300` 覆寫 A0 為完整 mask XOR1，恢復 caller frame 返回。

因此 `172b6 → 171de早返 → a2ee → 17300 → caller` 可由原指令完整串接，不需要替未知 callee 假造返回。這條路徑最深 frame 為 caller_SP−32；先前 `171de` 的 nested frame 也各自恢復。

其他 mode/config5 路徑仍在 `0xa2ee` 入口停止。本批不是完整 `0xa2ee` 合約驗證。`0x13d48` 也只驗證入口；另4組 bit1 返回測試明示假設它保存 live S1、SP/GP/frame，故意破壞 A/T及S0，再執行原 epilogue。這4組不證明該 callee 的實際保存行為。

## callback 寫 GP+172 後的事件 gate

先執行原 `0x9f7a`，保留其 GP+172 寫入，再由 fixture 輸入另一個 bit0 事件。第二階段明示設定 enabled=1、config3=15、extra=1、config8=16；這是 **兩次明示先後執行**，不是已證明的 callback 投遞事件。

後續原 `0x171de` 會實際執行 `0x9fc2` 讀 GP+172：

- callback 寫0：排程早返，繼續走上述自然 handler 返回。
- callback 寫1：到達未知取樣 provider 入口，停止。

1536組涵蓋 callback 的 config bit4開/關、ready={0,1,255} 與完整256個K；第二階段不覆寫 FLAG。這保留先前發現的「非零偶數 K 仍產生1」，並驗證該結果確實可被原排程 gate 讀取。尚未證明實機事件順序、provider 綁定或並行狀態穩定性。

## `0x9fb2 → 0x17320` 先清 pending 再看 enable

`0x9fb2` 先讀 `U8[GP+174]`；為0時無 frame，返回傳入 A0。非零則**先清 GP+174，再無連結尾跳 `0x17320`**。

`0x17320` 建 frame16只保存RA，執行原 `0x8440` 讀 `U8[GP+364]`：

- enable=0：恢復 frame，返回0，不讀 task/provider。前面清掉的 pending 不會恢復。
- enable非零：先恢復 caller RA，再讀 `[0x40050]`，再讀 `U8[GP+365]`，設 A1=1，恢復SP後尾跳。A0為 task 完整byte；T1為載入的target，A2等未設定的參數保持輸入。

注意這裡 task 是 **GP+365**，callback 表系統則是 GP+166。不能因兩者使用相同服務槽位便合併兩個 task byte。

## 驗證

[test_v4160_task_event_cpu.py](test_v4160_task_event_cpu.py) 使用明確 `check()`；一般模式與 `-O` 均保留檢查：

```text
python analysis/test_v4160_task_event_cpu.py
python -O analysis/test_v4160_task_event_cpu.py
```

輸出：

```text
PASS: 65536 event masks {'schedule': 32768, 'bit1': 16384, 'none': 16384}; 6144 config/clamp cases; 65536 full mode/config8 pairs; 6912 original gate chains {'sample': 2560, 'handler': 4352}
PASS: 1536 callback/separate-event state chains; 4 explicit bit1 returns; 65536 pending/enable pairs; 65536 direct enable/task pairs; 4 mutations
PASS: mode1/config5-low2=3 handler returns by original instructions; exact accesses/stores/frame; providers NOT executed
```

65536 mask 窮舉只涵蓋 **16-bit入口分類與callee邊界**；完整32-bit高位另由選定的原 handler/返回案例驗證，不代表窮舉32-bit狀態。6144組為全部 config3 byte × config8={0,3,4,15,16,255} × mode={0,1,2,255}；另完整mode/config8 byte矩陣採config3=15。所有步驟核對完整資料存取與stores順序、frame及返回暫存器。

四組記憶體內 mutation：bit0測試改測bit2、clamp上限3改2、返回XOR1改XOR2、pending store移至鄰byte。第一組用mask=3，在所有合法callee/return邊界停止，確認由選錯入口檢查拒絕；不使用未知位址執行錯誤作偵測。其餘分別由參數、返回值或存取序列檢查拒絕。原BIN未修改。

區段 SHA-256（右界不含）：

| 原區段 | SHA-256 |
|---|---|
| `172b6..17320` | `e792a1c7fb2470f57842d7664cf690fab8b26c8cd4b431a5ba136cccf7ed34e9` |
| `17320..17344` | `ecc625cbfd6f7e3e164ccde1391a8ef33b7e351ce1680529daf971b53c41dd1a` |
| `9fb2..9fc2` | `26b77ac789bb966bce58e627c3f7e7a77589809412c6ff26a606f0fd4c4dd665` |
| `a2ee..a316` | `4b3228fc050d92c63cd897c7f54e162e89f203af7fbd457235457ccf013e4232` |
| `a372..a37c` | `5337349bd213a4afedd4bb2b40e85f8a135ca2a3ee774b3c2da607774b084509` |

後續待核對完整 `0xa2ee`、`0xa204`、`0x10816` 與 bit1 的 `0x13d48`，以及實際 provider、payload 保存與事件投遞合約。仍不宣稱實機可達性、IRQ行為或完整啟動已證明。
