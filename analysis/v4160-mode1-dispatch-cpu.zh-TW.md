# v4.1.60 mode 1：58 個 ID 與第一個呼叫邊界

2026-11-26。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。從 `0x14d2e` 執行原 getter、七項跳表、mode 1 ID 樹及必要的參數／frame 指令；在第一個 callee、tail target 或 `0x152f4` 狀態 handler 入口停止。只用本機合成記憶體，不操作設備。

## 範圍與共同前提

mode 由原 `0x829e` 的 `U8[0x2000bfb5]` 讀取得到，fixture 設為 1；跳表仍使用原 APP 的 `0x1a6b8`。mode 1 讀一次 `U16[record]`，共識別 58 個 ID。除六個條件 ID 外，第一個停止點前不再讀 record 的其他 byte。

未識別 ID，或識別後條件拒絕時，透過 `0x14da2` 返回 caller：A0=`0x1a6bc`，不是零。S0／RA／SP 恢復，讀回順序為 RA→S0。所測全部路徑只做入口保存 S0、RA 的兩項 stores；record、mode byte 與其他資料均不改寫。

以下 ID 均為十進位，P=原 record 指標。「tail」表示 A0=P、frame 已恢復、RA=caller link；「call」表示 frame 尚在、SP=`caller_SP-16`、S0=P、RA=表內 continuation。所有 target 函式體均未執行，不能推論其保存合約或完整功能。

## 直接 tail

| ID | target | ID | target |
|---|---|---|---|
| 130 | `0xd288` | 259 | `0xdac8` |
| 280 | `0xcf96` | 297 | `0x10440` |
| 325 | `0xd632` | 505 | `0xdbcc` |
| 524 | `0xb390` | 568 | `0xabc4` |
| 579 | `0xb2fe` | 599 | `0x10288` |
| 602 | `0xd104` | 605 | `0xd332` |
| 659 | `0xb1b6` | 694 | `0xb14a` |
| 737 | `0xda74` | 755 | `0xb402` |
| 799 | `0xd14a` | 801 | `0xb372` |
| 819 | `0xd378` | 825 | `0xf0d0` |
| 826 | `0xd47c` | 880 | `0xa054` |
| 921 | `0xb036` | 923 | `0xb05c` |
| 925 | `0xd64a` | 950 | `0x10044` |
| 984 | `0x10096` | 994 | `0xc3d4` |
| 995 | `0x100d6` | 1022 | `0xd69c` |
| 1025 | `0x13bd2` | 1029 | `0xd1b2` |
| 1267 | `0x185d8` | — | — |

另兩個 tail 到 `0x10100`：ID 614 指定 A1=1；ID 741 指定 A1=0；兩者 A0=P。其他直接 tail 的 A1／A2 保持入口值，未補造參數。

## `0x82a8` 的兩種進入方式

以下均指定 A0=0、A1=index、A2=P，但 call 與 tail 的 frame／link 不同：

| ID | index | 進入方式／RA |
|---|---|---|
| 258 | 0 | call，`0x15072` |
| 306 | 1 | tail，caller link |
| 627 | 2 | call，`0x14e70` |
| 658 | 3 | tail，caller link |
| 692 | 4 | tail，caller link |
| 947 | 8 | call，`0x151c0` |
| 978 | 11 | tail，caller link |
| 991 | 12 | tail，caller link |
| 1001 | 13 | call，`0x15238` |
| 1013 | 15 | call，`0x14ff6` |
| 1657 | 18 | call，`0x152c4` |

本批停在 `0x82a8`，沒有執行其槽位 wrapper 或 copy provider；不把索引參數解釋成已完成資料複製。

## 其他第一個 call

| ID | target | RA | 已指定參數 |
|---|---|---|---|
| 553 | `0xcec0` | `0x150c4` | A0=P |
| 585 | `0xc8a2` | `0x150e2` | A0=P |
| 820 | `0x1083c` | `0x15190` | A0=`0x1069e`、A1=P |
| 963 | `0xc472` | `0x14f94` | A0=P |
| 1656 | `0xff56` | `0x15050` | A0=P |

這些均保留 outer frame。本批沒有替 callee 供給合成返回，也沒有繼續其後的第二個 call／tail。

## 六個 byte 3 條件

這六個 ID 都先讀 `U8[P+3]`，未在本段檢查 record 長度或 tag：

| ID | 條件 | 第一個停止點 |
|---|---|---|
| 818 | `byte3&3==1` | call `0x82a8`，index=5、RA=`0x1516a` |
| 818 | 其餘 | tail `0xd3f6`，A0=P |
| 850 | `byte3&3==0/1` | tail `0x82a8`，index=6/7 |
| 850 | `byte3&3==2/3` | 普通返回，A0=`0x1a6bc` |
| 962 | `byte3&3==0/1` | call `0x82a8`，index=9/10、RA=`0x15208` |
| 962 | `byte3&3==2/3` | call `0xb730`，A0=P、RA=`0x151f2` |
| 1021 | `byte3&7==0` | tail `0x82a8`，index=14 |
| 1250 | `byte3&7==5` | tail `0x82a8`，index=16 |
| 1251 | `byte3&7==5` | tail `0x82a8`，index=17 |

最後三個 ID 的其他條件均普通返回。`0x82a8` 參數仍為 `(A0,A1,A2)=(0,index,P)`。ID 991 沒有 byte 3 guard；ID 923 是直接 tail，不能依相鄰程式猜測為條件分支。

## ID 2047 的本機狀態 handler

ID 2047（`0x7ff`）進入 `0x152f4`，本批在第一條指令前停止。此時還沒讀 byte 3，A0=`0x1a6bc`、S0=P、RA=`0x14d3a`、SP=`caller_SP-16`。後續狀態寫入與內部跳表仍待另驗；不能把本次未寫全域資料的結論延伸到其函式體。

## 獨立與 consumer 串接驗證

```powershell
python analysis/test_v4160_mode1_dispatch_cpu.py --standalone-only
python analysis/test_v4160_mode1_dispatch_cpu.py
python -O analysis/test_v4160_mode1_dispatch_cpu.py
```

獨立部分只需標準庫、原 APP、既有 outer／有限 CPU 模組。完整串接另用既有 consumer/filter/classification 模組及本機 SDK copy **參考候選**；`--carrier` 可指定路徑。候選長度、SHA-256、槽位與 body SHA-256 均先核對，候選資料不另行上傳。

```text
PASS: 65536 full-ID cases; 58 recognized IDs; 1536 conditional-byte cases; 174 length/tag probes; 3 mutations; callees/2047 state body NOT executed
PASS: 180 detached-consumer/mode1 chains; {'return': 12, 'tail': 127, 'call': 38, 'state': 3}; candidate-only copy; first-boundary stops
```

65536 組以 byte3=0 掃描全部 16-bit ID，從實際額外 byte 讀取或非返回停止點取得的 census 必須與 58-ID 清單一致。六個條件 ID 另外各測全部 256 個 byte3，共 1536 組。174 組為每個已識別 ID 配對三種 `(length,tag)`：`(0,0)`、`(8,2)`、`(255,255)`，byte3=5。這些直接 fixture 只驗證本段讀取與參數，不聲稱長度 255 可由正常 ingress 到達。

每次檢查精確 reads／stores、第一個停止點、A0–A2、link、frame 與其他未使用暫存器；未知指令或錯誤存取直接失敗。三項記憶體複本變異分別更改 ID 819 比較、index 0 參數及 byte3 mask 3→7，必須由 endpoint／參數 oracle 抓出，不能靠解碼錯誤充當通過。

180 組串接使用 58 個已識別 ID 加上兩個未識別非零 ID，各配 byte3=0／1／5。原 consumer 執行 snapshot copy、清除 slot 17 ID、合成 CSR 與原 filter；分類只為未知 `0x81aa` 提供正常返回 1（保存 SP／S／GP／記憶體並改寫 caller-saved 暫存器）。隨後 mode getter 與 mode 1 都執行原碼。12 組普通返回繼續原掃描至 caller；127／38／3 組分別停 tail／call／本機狀態入口。逐例核對完整 queue、snapshot、CSR=0x88、copy 控制 word 恢復。

候選 copy 不證明實際 provider 綁定；其餘 callee 均未執行，也未推論實體設備、IRQ 或完整功能。原 APP 與共用 CPU 未改。既有 `feature_dispatch_tree.c`／`feature_dispatch_handlers.c` 已包含這些 C 重建，本批增加原指令驗證，沒有新增重建 bytes 或重算覆蓋率。後續優先追查 ID 2047 狀態流程及這批 call／tail 的實際合約。
