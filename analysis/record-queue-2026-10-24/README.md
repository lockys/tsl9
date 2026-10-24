# 記錄佇列、回呼建構與編碼

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/record_queue.c)：原廠 `1787C–1798A` 共 **270B／94 指令／14 架構區塊**。C11／C++17 的246個非控制bytes與7個具型別控制參照，經純資料原位址編碼後全270B與原BIN相同。[正式收據](evidence/standalone-trial.json)

## 已確認的靜態行為

- `1787C` 保留16B frame。兩次fresh count讀取的原AUIPC位址同為 `2000C8AE`；第二次值大於15時略過複製。
- `1789A` 的原AUIPC表達式指向 `2000C8AC`。使用then-live S0，複製參數為目的 `S0+3+7*byte[S0+1]`、來源原A0、長度7，間接透過 `4004C`。
- 呼叫後重新讀取then-live S0+1／+2，分別遞增索引並遮罩15、遞增計數，再以原AUIPC表達式寫回。then-live S1決定正常還原返回，或先還原16B frame，再以A0=255無link尾跳 `17666`。
- `178F8` 保留32B frame，以值0／長度7參數呼叫表項 `40048`，依原順序做word／halfword／byte遮罩與寫入，再呼叫1787C。
- `17948` 無frame。以A0低6 bits更新記錄bits10..15，設定byte6 bit7；依A1選擇返回、直接尾跳1787C，或先將+4 halfword OR 1F00再尾跳。

上述配置支持「16槽／7B記錄環形佇列」推論，但**複製前的索引沒有本地遮罩**。呼叫後的 `&15` 不能證明先前存取有界；初始索引／計數、memory ownership及callee對S0／S1的影響仍未證明。保留原存取，沒有擅自加入清零或界限修正。

## 真實整合與限制

1787C的待解析參照已綁到真實30B入口，全部270B一起連入；新增17666依賴，所以直接UND仍為17。元件為 **3000B code＋456B data、270個非零FUNC、11個入口alias、238 RELA**；前一階段2730B code／456B data與62個非零向量綁定均保留。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

正式版本採trial-v2。首次trial-v1中，組譯器把原4B ADDI縮為2B而未通過；原輸出保留本機、未宣稱成功。現行asm port明確保留4B寬度。

SDK預設表項對應memcpy／memset，但不是已安裝callee的證明。[對照](rom-profile-correspondence.json) 元件仍是VMA0 ET_REL；包括178F8在內的原始literal callback位址仍依賴最終原位址配置，不能把診斷物件當成已連通的執行時回呼。

`src/`現有89個C/H，code來源比對124組／248物件；指標資料另2組／4物件，合計 **126組／252物件**。這不證明完整行為、實機ROM／記憶體／啟動／IRQ或BLE OTA相容性。

## 後續與功能候選

[下一組有界反組譯](next-17666-frontier.json)涵蓋17666–1787C的534B／187指令，包含17666／176A0／176F8候選入口。它參照已存在的90B0／9124及尚待確認的1753A／C776，後續應重用實際定義，避免重複連結。

可探索唯讀離線記錄／佇列檢視器，呈現原始索引、計數、遮罩與尚未證明的界限；目前僅研究候選，尚未加入韌體。

本輪沒有目標／HOST model／ISA或ESIL執行、硬體／網路操作、新BIN、commit或push。[建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
