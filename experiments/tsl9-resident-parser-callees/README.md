# Parser callees、RAM helpers 與訊息建構

[English](readme.en.md) · [完整 caller parser](../tsl9-resident-task-parser/README.md) · [保留 callback 條件證據](../tsl9-original-callback-provenance/README.md)

[C/C++](resident_parser_callees.c) 新增 **16 個完整本體／2,492 CODE bytes／940 指令**。實際 C11／C++17 物件相同，191個正尺寸FUNC、174 relocations（126 direct controls＋24組HI／LO）；原位址正規化後每個byte相同。92個Xwchc ports依primary encoding definitions／52個官方正例核對。這是原context重建，並非恢復出的原廠C原始碼。

補上的四個原 parser 缺口為 `0x5E950`、`0x5EA9A`、`0x5EACA`、`0x5EE06`，實際 callsites 為 `0x5F37C`／`0x5F512`／`0x5F88A`／`0x5F93C`。另包含其真正需要的 `0x5ECF6`、`0x5E4B0`、兩個尾跳入口、兩個訊息builder與六個RAM本體；鄰近但不在此呼叫鏈上的函式未選入。

## ROM來源與RAM執行位址

| 執行範圍（半開） | 候選ROM來源（半開） | Bytes |
| --- | --- | --- |
| `0x2000202C..0x20002078` | `0x4229C..0x422E8` | 76 |
| `0x20002078..0x200020B6` | `0x422E8..0x42326` | 62 |
| `0x200020B6..0x200020F4` | `0x42326..0x42364` | 62 |
| `0x200020F4..0x2000218A` | `0x42364..0x423FA` | 150 |
| `0x20002276..0x200022BE` | `0x424E6..0x4252E` | 72 |
| `0x200022BE..0x20002426` | `0x4252E..0x42696` | 360 |

六個完整本體共782 bytes，均在前輪loader的完整first copy內：source `0x402B0`、destination `0x20000040`、last destination word **inclusive `0x20002E70`**、長度11,828，exclusive end `0x20002E74`。所有分支與兩個RAM→ROM HI／LO calls都按實際執行PC核對；沒有把ROM副本位址當成執行位址。這仍是候選loader關係，**不是實機ROM身分或RAM相容性證明**。

## 原始控制與存取寬度

所有16個CFG的指令皆可到達，自身frame在正常出口平衡；保留RET後仍可到達的分支與真正的tail exits。`0x6A730`／`0x6A796` 各只有4 bytes，分別無link尾跳 `0x52418`／`0x527FA`，未選入旁邊其他wrapper。

lookup roots會fresh讀 `0x20003484` 或 `0x2000347C` 的list head；其數值位址也對應前輪initializer的word-zero requests，但**未觀測實際list、node內容、終止或alias安全**。相關比較與鏈結邏輯完整保留，沒有新增遍歷上限。

`0x5EA9A` 對同一record+84先讀byte gate，再於需要時讀word作引數，record+88亦保留word寬度；正常返回值經原SNEZ／literal1路徑限制為0..1。部分early returns不配置frame，呼叫路徑自身frame為16；沒有把這些不同寬度與控制流合併成猜測的struct欄位。

`0x200022BE` 從 `0x20003504` 取得base pointer，保留對base+0先寫word256、再寫word0的順序，以及後續原始輸入／輸出存取。它沒有callee或自身frame。RET後的 `0x20002422` NOP／`0x20002424` 跳回 `0x200023AC` 仍可到達，完整保留；**實體周邊、操作語意及重試終止仍未確認**。

## 訊息配置與尚未證明的邊界

兩個真正的builders各配置48-byte自身frame，呼叫前輪實際message allocator；配置null時走原restore／RET，非null路徑保留copy requests、釋放frame，再尾跳前輪 `0x43208` send：

| Builder | 配置請求 | 原copy requests與限制 |
| --- | --- | --- |
| `0x52418..0x524B0` | 49 bytes | allocation+10／6 bytes；+17／incoming A3全32位長度；最後寫byte+48 |
| `0x527FA..0x528B6` | 24 bytes | body=allocation+8；body+2／6 bytes、body+9／6 bytes；stride16 |

第一個builder把length的低8位寫至allocation+16，但copy使用完整32位incoming A3；**尚未證明每個caller都保證copy長度範圍**。數值上17+32=49，length32時會涵蓋最後+48 byte，原程式之後再寫該byte；沒有新增clamp、padding或改變順序。

第二個builder的原header word為 `0x010B3E91`，encoded byte3 count為1，但loop仍fresh讀取該byte。只有header穩定、有效memory／copy／private-callee與無非同步alias等條件成立時，才能推得單次16-byte body迭代；**沒有把原loop改為常數一次，也沒有宣稱實機heap安全或訊息交付成功**。

## 組合、驗證與使用

[callees_abi.c](callees_abi.c) 只編譯驗證RV32 widths、來源映射、frame slots與配置數值；C／C++物件相同且allocated bytes=0，沒有runtime provider。

實際非載入ET_REL組合為 **27,594 CODE＋256 DATA／9,520指令**，1,821正尺寸FUNC、1,423 relocations。所有input bytes／symbols／relocations完整保留，原始CODE位址不重複，兩個獨立ELF readers一致。四個真實缺口已補上，具名依賴 **11→7**；本輪7個imports均有前輪真實provider，沒有新增具名缺口、stub或opaque call。其他numeric CODE pointers／callback／memory／IRQ效果仍未因此封閉，前輪callback條件證據已重新驗證且未改寫。

[證據](evidence-v1.json) · [完整驗證](audit-result-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-resident-parser-callees/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需要固定本機APP／SDK、前輪native artifacts與Windows NDK LLVM；無下載，其他平台未驗證。APP保持159 C/H、95.54%位元組覆蓋率，**不是功能完成率**。4-byte啟動來源缺口及ROM／RAM／ISA／IRQ／Flash／OTA相容性仍開放。

未連入APP、未產生BIN，沒有target／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。後續唯讀lookup／source-map／copy限界診斷仍是未實作UI候選，不讀取或公開live records、keys或MAC contents，不修改live state。
