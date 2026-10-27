# 完整 task parser、排程記錄與 masked bit count

[English](readme.en.md) · [前輪 task／message chain](../tsl9-resident-task-transition/README.md) · [原 caller](../tsl9-resident-callback-registration/README.md)

[C/C++](resident_task_parser.c) 新增 **4 個完整本體／2,316 CODE bytes／770 指令**。實際 C11／C++17 物件相同：170 個正尺寸 FUNC、140 relocations（120 direct controls＋10組 HI／LO），原始位址正規化後每個 byte 相同。27 個 Xwchc ports 依原始 encoding definitions／52 個官方正例核對。保留 original register/control ports，並非恢復出的原廠 C 原始碼。

| 完整範圍（半開） | Bytes／指令 | 自身 frame | 本輪研究內容 |
| --- | --- | --- | --- |
| `0x5F234..0x5F96C` | 1,848／597 | 112 | 原 task 的完整 parser 與所有後段分支 |
| `0x43414..0x43520` | 268／97 | 48 | 掃描、配置與串接排程記錄 |
| `0x43A14..0x43A8C` | 120／43 | 32 | 依 ID 計算 stop-task 參數及清除記錄 |
| `0x57AD8..0x57B28` | 80／33 | 0 | 五個 byte 中32＋5有效位元的計數 |

每個 CFG 的所有指令均可到達，自身 frame 在正常出口平衡。前輪512-byte parser視窗並不完整；本輪包含 RET `0x5F322` 後仍可到達的分支，直到最後 `0x5F96A` 跳回 `0x5F8DA`。相鄰 `[0x5F96C,0x5F98E)` 的34 bytes不從此 root可達，屬於另一個 frame0函式，未選入。

## Parser 的實際 caller 與依賴

原 task `0x60516` 在 `0x606F8` 保留 record argument，`0x606FE` 呼叫本輪 `0x5F234`。原 buffer pointer為record+120，receive-status provider仍為前輪實際 RAM `0x2000263A`；原 low-nibble／length／field 分支、copy／compare requests、64-bit arithmetic helper與 callback ports完整保留，未執行 parser或產生測試封包。

本輪補上原缺口 `0x5F234` 與三個實際 callee，同時暴露四個**真正尚缺的深層本體**：`0x5E950`、`0x5EA9A`、`0x5EACA`、`0x5EE06`。它們只保留為原始呼叫的具名 imports，沒有 stub，也沒有宣稱其效果已知。其他7個 imports均有前輪真實 providers。

| 真正的間接 call PC | Fresh pointer slot |
| --- | --- |
| `0x5F6D6` | `0x20003234` |
| `0x5F708` | `0x200031E0` |
| `0x4346C` | `0x200031E0` |
| `0x434AA` | `0x20003220`（配置失敗路徑的 optional callback） |

四個 compressed JALR-through-A5的原 bits與載入關係均已核對；callback實際值、目標、返回與副作用未證明，不用猜測的直接 provider取代。

## 排程記錄的數值契約

`0x43414` 保存 `0x4002420C` word、寫0、FENCE.I，再保留各結果路徑的 restore requests。它從 `0x2000322C` 取得 record-array pointer，以 **12-byte stride掃描16個 entries**；遇可用 entry時請求配置16 bytes。成功後保留 node/list與record stores、optional輸出 index；encoded results為2／11／8／0。串列next位於node+12，原遍歷沒有 cycle上限，終止與 alias安全未證明。

`0x43A14` 保留原 **ID 0..47** 檢查，以12-byte stride讀記錄；entry非零時呼叫前輪真實 `0x439A8` stop-task，task ID=`ID >> 4`，event=`low16(1 << (ID & 15))`，再清除entry+0／+4兩個word；沒有明確清除第三個word。encoded results為0／2。

兩個函式的數值界線不同：16×12=192、48×12=576。保持原樣，**未證明兩者共用同一容量、實體 RAM 所有權或完整排程相容性**。控制 word 的 save／zero／FENCE.I／restore請求也不代表已證明硬體原子性或中斷隔離。

## 32＋5-bit 計數

`0x57AD8` 依offset **1／2／4／0／3**讀五個unsigned bytes。前四個byte組成32-bit值，第五個byte只保留低5位；原兩個loops分別訪問32與8個bit位置，後者高3位因AND31為0。unsigned8 accumulator的條件結果範圍為 **0..37**，不會在此數值上限下溢位；沒有 callee、CSR或自身frame。

這是原始指令與loop counters導出的數值結論，沒有執行HOST model／ISA或合成輸入。需要有效原始記憶體存取；五次load不是已證明的原子snapshot。**尚未證明這五個bytes是實機BLE channel map或具有其他特定領域含義。**

## 驗證與使用

[parser_abi.c](parser_abi.c) 只編譯驗證RV32 widths、112／48／32-byte frame slots、192／576-byte數值範圍及37-bit上限；C／C++物件相同，allocated bytes=0，沒有runtime provider。

實際非載入ET_REL組合為 **25,102 CODE＋256 DATA／8,580 指令**，1,630正尺寸FUNC、1,249 relocations。所有input bytes／symbols／relocations保留、原始CODE位址不重複，兩個獨立ELF readers一致。原8個具名缺口減去已補的parser，再加四個真實深層缺口，結果為 **11**；這反映更完整的呼叫關係，並非已完成相容性。四個opaque sites原樣保留，transitive／memory／IRQ效果仍開放。

[證據](evidence-v1.json) · [完整驗證](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-task-parser/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機APP／SDK、前輪native artifacts與Windows NDK LLVM；無下載，其他平台未驗證。APP仍159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口、實體ROM／RAM／ISA／IRQ／Flash／OTA相容性及binding前無dispatch仍開放。

未連入APP、未產生BIN，沒有target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。唯讀離線37-bit mask／排程記錄診斷是後續功能候選，尚未實作，不修改live callbacks、RF或記錄。
