# v4.1.60 `0xb6f4` 入口與 `0xfe6a` 首個服務邊界

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本批在本機有限 CPU 執行原指令與合成資料，沿上一批 `0xcd6a` 的實際 call／tail 接續；不操作設備、不替 opaque callee 指定返回。

## `0xb6f4`：低 byte guard，完整值傳入 callee

guard 等價於「入口 A0 的低 byte 在 1–18」，原式是 `((A0-1)&255)<=17`，不是完整 32-bit 值限制為 1–18。

- 拒絕：直接返回，A0 保持原值，不建立 frame、不寫資料。
- 接受：建立 16-byte frame，依序保存 S0、RA 至 caller_SP−8、−4；S0=完整 A0，呼叫 `0x171de`。入口 RA=`0xb70e`、SP=`caller_SP-16`、A0 仍是完整輸入。

例如 `0x101`、`0x10001` 會通過，並未先截成 1 傳給 callee。本批停在 `0x171de` 第一條指令前。後續 `0x9fc8` 選擇使用完整 S0 的比較，最終 byte store 為 `0x2000bf0c`，但這些後段尚未執行；不把入口 guard 的語意延伸成 callee 返回後合約。

## `0xfe6a`：設定 gate 與三個原 getter

I=入口 A0；fixture GP=`0x20004000`。總是先讀 `[GP+84]` pointer cell，再讀 config+9 的 byte。F=`byte&12`：

- F=0：不建立 frame、直接返回，A0=I。
- F非零：依序保存 S0／S1／RA 至 caller_SP−8／−12／−4，frame=16 bytes，S0=GP+84（pointer cell 位址），S1=I。

三個 getter 均直接執行 APP 原碼，沒有 stores，其他暫存器保持：

| getter | 資料來源 | A0 |
|---|---|---|
| `0x828c` | Q=`U8[0x2000bfb4]` | Q≥4 時 1，否則 0 |
| `0xa9de` | T=`U8[0x2000bedc]` | 完整 byte |
| `0x81ee` | E=`U8[0x2000bed5]` | 完整 byte |

F非零時先執行 `0x828c`。Q<4 即恢復 frame 返回 A0=0；其餘分支如下。令 X=`U8[GP+292]`、Y=`U8[GP+288]`：

| 條件（均已有 F非零、Q≥4） | 結果 |
|---|---|
| I=0、X=0 | 返回 A0=1 |
| I=0、X非零且≠2 | store GP+292=0，返回 A0=1 |
| I=0、X=2 | call `0x90b0`，A0=`0xfb1e`、RA=`0xff2e` |
| I非零、T∈{1,7}、X非零 | 返回 A0=T |
| I非零、T∈{1,7}、X=0 | call `0x81b0`，A0=T、RA=`0xfea8` |
| I非零、T不在{1,7}、X=0 | 返回 A0=T |
| 同上但X非零、Y非零 | 返回 A0=T |
| 同上但Y=0、E非零 | 執行原 `0x81ee` 後返回 A0=E |
| 同上但E=0 | call `0x81b0`，A0=0、RA=`0xff00` |

讀取也是有條件的：I=0 只讀 X，不讀 T／Y／E；I非零先讀 T 再讀 X，僅 T不在{1,7}且X非零才讀 Y，Y為零才讀 E。到本批停止點前，不讀 GP+291／GP+296，也不寫它們。唯一的全域 store 是表內 GP+292 清零。

普通返回按 RA→S0→S1 讀回 frame。兩種 opaque call 都保留 frame：SP=`caller_SP-16`、S0=GP+84、S1=完整 I；A1 及其他未用暫存器保持。本批不執行 `0x81b0`／`0x90b0`，也未執行傳入位址 `0xfb1e`；因此不宣稱已取得時間值、安裝 callback 或完成後續狀態更新。

## 從原 `0xcd6a` 延伸的控制流

同一 CPU 從上一批 `0xcd6a` 執行至原 call `0xb6f4` 或 tail `0xfe6a`，保留當下暫存器與記憶體，直接續跑本批原指令。此處是 APP 真正的 call／tail edge，不是把兩個獨立入口任意安排為資料流序列。

1152 組涵蓋六個 GP+357 狀態（0／1／5／7／10／255）、四個 category、兩個輸入、四個共享 getter byte 與六組 downstream 設定：

- 576 組在原 `0xcd6a` 返回。
- 432 組經其原 call 到 `0xb6f4`，A0=6／7，繼續停在 `0x171de`；兩層 frame 都仍在，最內 SP 比最初 caller 低 48 bytes。
- 112 組經其原 tail 到 `0xfe6a`，再返回最初 caller。
- 32 組經原 tail 到 `0xfe6a`，停在 `0x81b0`。

`0xcd6a` 真正 tail 到 `0xfe6a` 時固定傳 A0=1，因此這組串接不會走 I=0 的 `0x90b0` 分支；該分支由獨立矩陣覆蓋。仍未證明更上游 ingress、實際排程或所有 caller 的可達性。

## 重現與結果

```powershell
python analysis/test_v4160_downstream_gates_cpu.py
python -O analysis/test_v4160_downstream_gates_cpu.py
```

只需標準庫、原 APP 與既有有限 CPU／state consumer 測試模組；不需 SDK carrier、copy binding 或 callee 合成返回。

```text
PASS: 1280 guard aliases; 131072 config/readiness cases; 131072 type/active cases; 65536 stage/event pairs; 1536 full-width probes; 3 mutations; actual getters; opaque callees NOT executed
PASS: 1152 actual cd6a-to-downstream control-flow chains; {'gate_return': 576, 'guard_call': 432, 'feature_return': 112, 'feature_timer': 32, 'feature_callback': 0}; no SDK or callee return hypotheses
```

| 組數 | 矩陣 |
|---|---|
| 1280 | 五組高位 prefix × 全部低 byte，核對 `0xb6f4` guard 與完整 A0／S0 |
| 131072 | config byte × Q 全值 × I=0／1 |
| 131072 | T × X 全值 × I=0／1 |
| 65536 | Y × E 全值，固定 I非零、T=0、X=1 |
| 1536 | I=`0x10000`／`0xffffffff`，配指定設定／狀態／getter 邊界 |

逐例核對原 getter 的參數、link、frame、保持暫存器與無 stores；並核對第一個停止點、精確資料 reads／stores、普通返回的 A0／frame、20-byte 全域 state 及相鄰 canary。三項記憶體複本變異分別改 config mask 12→8、Q門檻4→5、低 byte guard mask255→127；必須由 endpoint／getter結果斷言抓出，不能靠未知指令失敗通過。

原 APP 與共用 CPU 未修改。既有 native C 已重建這些區域，本批增加條件性原指令驗證，沒有新增重建 bytes 或重算覆蓋率。後續需追查 `0x171de`、`0x81b0`／`0x90b0` 的服務返回與副作用，以及返回後的 `0xb6f4`／`0xfe6a` 路徑。
