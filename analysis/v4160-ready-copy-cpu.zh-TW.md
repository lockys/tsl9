# v4.1.60：ready19 至固定資料複製與 128FE 入口

2026-11-26。接續 [19-byte 來源組裝](v4160-source19-cpu.zh-TW.md)：`D1B2` 讀到 `2000bf48` 的 ready byte 非零時，原 APP 設 A0=1 並尾跳 `12AD0`。本批沿此路徑，執行原 APP 軟體複製函式 `19BF0..19CA6`，確認送往 `128FE` 的 stack 資料與參數。

原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。全部在合成記憶體的有限 RV32IMC 解譯器中進行；未知下游 `128FE`、`1299E` 均在入口停止，provider、CSR、設備與實際傳輸未執行。沒有更動原 BIN、共享 CPU、seal 或既有 C。

既有 [record-copy-windows](record-copy-windows-2026-10-25/README.md) 已重建 94／106-byte 的來源 C 資料，既有 [memory-transfer](memory-transfer-2026-10-24/README.md) 也已重建完整 182-byte 軟體複製函式。本批補原指令資料流、逐次讀寫與條件性返回驗證，不將舊 C 工作算成新覆蓋率。

## ready 非零後選擇固定 94-byte 資料

令入口 SP=P、128-byte frame 起點 F=P−128，caller RA 保存於 F+124。

| 完整 A0 selector | 原 APP 路徑 |
|---|---|
| 0 | 呼叫 `1299E`，RA=12AEC；本批在該入口停止。 |
| 1 | 複製 `[19D08,19D66)` 的 94 bytes 到 F+4，然後呼叫 `128FE(F+4,94)`。 |
| 2 | 複製 `[19D68,19DD2)` 的 106 bytes 到 F+4，然後呼叫 `128FE(F+4,106)`。 |
| 其餘完整 word | 恢復 RA、SP 返回，A0 保留原 selector；不呼叫上述 callee。 |

`D1B2` 會將任意非零 ready byte 轉成 **完整 A0=1**，所以此鏈選擇固定 94-byte 資料。19-byte 組裝區的其餘內容沒有在這段讀取；也沒有從該區推導 94-byte 內容。

255 組案例覆蓋所有非零 ready byte，從原 `D1B2` 尾跳接入。另兩組從真正 `14D2E` 外層入口、mode 1、16-bit ID=1029 開始，沿原 ID 樹、恢復 frame、進 `D1B2` 再接至 `128FE` 入口。

直接 selector 測試包含所有 256 個 byte，以及 256、257、258、80000001、FFFFFFFF，共 259 個非 1／2 selector。這裡比較完整 word，不能以低 byte=1／2 取代原判斷。資料的實體功能與識別語意仍未命名。

## 原 19BF0 的每次讀寫

固定資料從捕獲的 APP bytes 讀取，不使用 provider 或合成來源填補。原軟體複製函式會依 source/destination 的模 4 對齊關係，選擇逐 byte、對齊 prefix、36-byte 批次、word tail 及 byte tail。

正常對齊 stack 時，94-byte 路徑為兩個 36-byte 批次、五個 word、兩個 byte；106-byte 路徑為兩個 36-byte 批次、八個 word、兩個 byte。完整兩個來源範圍均逐 byte 比對；不包含兩份資料之間的 2-byte gap。

36-byte 批次的順序是：

1. 先讀 source+0、+4、…、+28 的八個 word。
2. 寫第一個 destination word。
3. 再讀第九個 source word，即 source 指標遞增 36 後的 −4，等於舊 source+32。
4. 寫其餘八個 destination word。

因此不能把測試 oracle 換成一次 host slice 複製。54 組 live-overlap fixture 核對真正讀寫順序；其中 destination=source+32、count 至少 36 時，第一個 store 會先覆寫第九次 load 的來源，最後 destination+32 的 word 因而取到原第一個 source word。此為有界合成記憶體下的原指令結果，不宣稱通用 memmove 或實際記憶體 alias 合約。

另外 1776 組測試為 count=0..110 × source 模4 × destination 模4；檢查指定範圍內的精確讀寫寬度、位址、順序、值，並核對整個映射記憶體的寫入範圍。指標有效、可存取且不回繞是明示前提。沒有窮舉任意 32-bit 指標／長度或非正常存取。

共享 CPU 尚未實作此函式入口的 RV32 XOR；新測試只在 `19BF0` 處固定並處理精確原 word `00a5c7b3`，其餘指令沿用未更動的共享解碼器。這個局部入口處理不擴充為一般 XOR 解碼支援。

## stack 與下游返回邊界

24 組 selector 1／2 caller 案例覆蓋四個 stack residue 與明示 reply={0,1,FFFFFFFF}；residue 非零只用於有限存取驗證，不聲稱符合原 ABI 對齊要求。

原 caller 的本機寫入範圍只有：

- F+124..127 的 saved RA。
- F+4 起的 94 或 106 個資料 bytes。

F+0..3、資料後的洞位及 frame 外的映射記憶體保持入口值；不是把整個 128-byte frame 先填零。軟體複製保留 A0、RA、SP/GP 與所有 S 暫存器，允許其實際使用的 A/T 暫存器改變。

複製完成後，caller **重新設定** A1=94／106、A0=F+4，呼叫 `128FE`，RA=12B0A。測試在此檢查完整 stack payload，不執行 `128FE` 本體。

需要接回 caller epilogue 時，測試另明示下游正常返回，保存所有記憶體、frame、GP/SP 與 S 暫存器，破壞 A/T 並提供完整 A0 reply。其後執行原 12B0A→12AE2 的 epilogue，核對 caller RA/SP/S 全部恢復、A0 保留該 reply。這不是下游服務保存或實際操作成功的證明。

trace 納入原兩份 literal span 的資料讀取及非 APP 記憶體存取；既有 CPU 的指令 fetch 不列入資料 trace。本批沒有建立全 APP 的任意資料讀取或 writer census。

## 重現與 mutation

[test_v4160_ready_copy_cpu.py](test_v4160_ready_copy_cpu.py) 使用原 APP、已發布的 source19／mode1／feature_outer／zero_id_queue 測試依賴與標準庫；不需要 SDK carrier 或網路。

```text
python analysis/test_v4160_ready_copy_cpu.py
python -O analysis/test_v4160_ready_copy_cpu.py

PASS: 1776 count/alignment local-copy cases; 54 live-overlap cases; exact ordered reads/stores and preservation
PASS: 24 selector1/2 caller copies; 259 other selectors; 255 ready-byte chains; 2 actual mode1 chains
PASS: captured94/106 literal to stack to128fe; conditional normal return; 4 specified mutations; downstream/provider/hardware NOT executed
```

一般與 `-O` 均通過，檢查使用 `check()`。四個記憶體副本 mutation 改動 copy count、下游 count、第九個 load 的偏移、36-byte destination stride；均由指定參數或 ordered-access 檢查拒絕，不接受任意解碼／unmapped 例外作為通過。原檔未修改。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 12AD0..12B24 | `781e9b02bf9ab36ab17355a3a174050e377f960d7473c36ac4d7dc4da1d7de2a` |
| 19BF0..19CA6 | `7ad28bf9e3e203cdaf62539ed4dad2cb81ffe938f457ae43203a5868877836bb` |
| 19D08..19D66 | `88bd8a192643d363037b448c2707c53b3921fda53416859dfe96e08ddf057cde` |
| 19D68..19DD2 | `a1a8eb84eb3ad1e54c06631aeeebf1863dc26c1be369b3c67f05b670c66e58d3` |

後續待展開 `128FE` 的 112-byte 工作區、14 次迴圈與 `18BA2` 呼叫，以及 selector 0 的 `1299E`；實際 provider 身分、保存／寫入合約與設備相容性仍未證。
