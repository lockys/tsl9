# 記錄配置／控制路徑

[English](readme.en.md)

已重建原廠 `0x93AA–0x94EE` 的四個相依函式：**324B／109指令、19個架構區塊**。C11 與 C++17 原位連結的完整位元組均與原廠一致。選用來源在 [record_program.c](../../src/native/receive/record_program.c)；它含普通 C 記憶體／算術操作，以及必要的實體暫存器、frame、PC-relative與控制轉移埠，不能當成19個獨立 C ABI 函式。

| 原始範圍 | 已確認行為 |
| --- | --- |
| `93AA–93EE`，68B／19i | 讀取 `[[GP+84]+2]` 與 byte `2000BEC0`，條件式清除資料，再對 `40000400` 的16位元值設bit0 |
| `93EE–9410`，34B／12i | 半字寫 `FFFF→4000042C`、`0→4000043C`，再清除 `40000400` bit0 |
| `9410–9454`，68B／24i | 舊指標非零時呼叫 `[40068]`，清除 `2000BECC/BEC8`；以6×當下S0作為參數尾跳 `[40070]` |
| `9454–94EE`，154B／54i | unsigned19 guard、6B項目與終止項。暫存器維持入口值的條件下，一般項目為半字3000／40／80；大值分支寫3000／S0／0／0 |

兩個resident轉移的原始PC為`942A`（RA=`942C`）及`9452`（無新增link，使用已還原RA）。free／alloc與timer只是候選語意；實際ROM身份、記憶體有效性／所有權及周邊用途未證。S0／S1／SP在opaque呼叫後皆使用當下值，未假設被保存；入口guard不能證明後續最多19筆。8位計數器若與呼叫後S1無法相等，迴圈可能不終止。成功／失敗不同的restore次序及所有原始PC的AUIPC均保留。

真正接入前一元件後，結果為 **2250B／778i／127 strong FUNC／109 pending RELA／2 UND**；直接缺口剩`12ABE`與`14D2E`。診斷VMA0的AUIPC並不指向原廠RAM，控制relocation仍待解析，不能執行。既有1588B原位圖保持原樣；新324B原位圖另行證明，不冒算成完整韌體。已整理來源共66個C/H、40個native units；80組比較／160物件通過，之前78組結果及舊物件身份均未變。

v1來源曾因S0輸出引發保留SP錯誤；v2曾重排A3減法至A5=0之前。選用v3修正後通過完整位元組檢查。獨立審查另找出nominal FUNC owner漏檢；舊檢查器／收據保留，最新verify-v2每語言通過2600個負例，錯誤owner在兩語言均拒絕。IR及LLVM logs保留，未宣稱IR或LLVM語意證明。

[公開證據](publication-provenance.json)包括四份可攜原收據與一份只匿名化路徑的衍生收據。62份原始檔案保留本機ZIP並核對全部雜湊。BIN／APK及Git設定未變。本輪不執行目標、模擬ISA、操作硬體或產出韌體BIN。

值得後續考慮的是「呼叫後索引／長度一致性診斷」，但需要實際resident ABI與觀察資料；目前尚未實作。原機身份、installed ROM、完整啟動／記憶體／中斷與藍牙OTA仍未證明。

[重跑方式](../../experiments/tsl9-record-program/README.md) · [摘要](summary.json) · [獨立審查](independent-review.json)
