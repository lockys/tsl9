# Task 0x60516 剩餘 handlers 與排程索引分區

[English](readme.en.md) · [前輪 callees／RAM mapping](../tsl9-resident-parser-callees/README.md) · [原 task](../tsl9-resident-callback-registration/README.md) · [後續排程表配置關係](../tsl9-scheduler-allocation-contract/README.md)

[C/C++](resident_task_final_handlers.c) 新增 **5 個完整本體／2,254 CODE bytes／801 指令**。實際 C11／C++17 物件相同：187個正尺寸FUNC、163 relocations（143 direct controls＋10組HI／LO），原位址正規化後每個byte相同。53個Xwchc ports依primary definitions／52個官方正例核對。保留原context，並非恢復出的原廠C原始碼。

| 完整範圍（半開） | Bytes／指令 | 自身frame |
| --- | --- | --- |
| `0x5F98E..0x5FBAE` | 544／199 | 16 |
| `0x5FCDC..0x6014E` | 1,138／389 | 32 |
| `0x6014E..0x6020A` | 188／74 | 16 |
| `0x5FBAE..0x5FC70` | 194／66 | 32 |
| `0x43874..0x43932` | 190／73 | 48 |

三個原缺口分別由 task `0x60516` 的 `0x6068E`／`0x60620`／`0x605AC` 呼叫。兩個helpers是實際callee；鄰近 `0x5FC70`／`0x6020A` 等其他函式未選入。所有CFG指令可到達、自身frame在正常出口平衡，早期RET後的分支完整保留。

## 原frame釋放後的parser尾跳

`0x5FCDC` 有一般返回與一條無link parser tail：`0x60016` 保留record argument，恢復原RA／saved registers，`0x60028` 釋放32-byte frame，`0x6002A` 再跳至前輪完整 `0x5F234`。原JAL-zero bits、參數與順序均已核對，沒有改成一般C call或留下額外frame。

完整原 task 的 **13個可解析編碼call sites** 均已有本輪或前輪provider，該task本體未發現其他未解析間接call site。這不涵蓋所有numeric CODE pointers、之後的callback dispatch、transitive memory／IRQ effects或實機成功狀態，**不是runtime closure**。

## 釐清原16／48索引界線

前輪已保留 `0x43414` 的0..15掃描與 `0x43A14` 的0..47 removal。本輪 `0x43874` 顯示另一路掃描16..47。三者都fresh讀取numeric pointer slot **`0x2000322C`**，使用 **12-byte stride**：

| 原函式 | 數值索引範圍 | 相對table base的半開存取extent |
| --- | --- | --- |
| `0x43414` | 0..15 | `[0,192)` |
| `0x43874` | 16..47 | `[192,576)` |
| `0x43A14` removal | 0..47 | `[0,576)` |

在pointer穩定、有效memory與原private-callee契約等條件成立時，兩段索引數值上沒有gap／overlap，合計 **48×12=576 bytes**。**尚未證明實際配置576 bytes、所有權／生命週期、各呼叫間pointer相同，或併發安全**；不從索引常數推定實體RAM容量。

新helper對空entry形成 `low8(ID >> 4)` 與 `low16(1 << (ID & 15))` 引數，呼叫前輪 `0x43728`。原條件為其返回非0才寫入兩個record words及optional byte-width ID，返回0則繼續掃描；沒有套用猜測的通用SUCCESS值。helper本身的encoded outcomes為0／2／8，不代表已觀測的硬體計時或事件交付結果。

它保存 `0x4002420C` word，寫0、FENCE.I，再保留各結果路徑的restore requests；**硬體原子性與IRQ隔離仍未證明**。原packet欄位寬度、比較／copy／range／peripheral requests全部保留，沒有執行packet或產生合成輸入。

## 組合與使用

[handlers_abi.c](handlers_abi.c) 僅編譯驗證RV32 widths、原frame slots、索引分區及576-byte數值union；C／C++物件相同，allocated bytes=0，沒有runtime provider。

實際非載入ET_REL組合為 **29,848 CODE＋256 DATA／10,321指令**，2,008正尺寸FUNC、1,586 relocations。所有input bytes／symbols／relocations保留，原始CODE位址不重複，兩個獨立ELF readers一致。三個真實缺口已補上，具名依賴 **7→4**；本輪13個imports均有前輪真實provider，沒有新增具名缺口、stub或opaque call。四個剩餘具名缺口來自另一個 `0x58C52` callback：`0x58498`、`0x58788`、`0x588B4`、`0x58988`。

[證據](evidence-v1.json) · [完整驗證](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-task-final-handlers/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機APP／SDK、前輪native artifacts與Windows NDK LLVM；無下載，其他平台未驗證。APP仍159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。前輪callback／RAM mapping條件證據重新驗證，沒有改寫為live hardware結論；4-byte啟動來源缺口與ROM／RAM／ISA／IRQ／Flash／OTA相容性仍開放。

未連入APP、未產生BIN，沒有target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。唯讀排程bank／static-call來源診斷仍是未實作UI候選，不修改live table、callbacks或registers。
