# Mode 查表資料正式整合

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 來源](../../src/native/receive/record_mode_row_data.c)

將條件 mode 1／3 的兩列唯讀資料納入 `src/`、manifest 與原位址連結，共新增 **32 bytes**。C11／C++17 診斷 ELF 相同，**73,510／76,800 bytes（95.72%）** 與官方 BIN 原位址逐 byte 相符：69,412B CODE＋4,098B DATA。這是靜態位元組覆蓋率，不是功能完成率。

| 項目 | 證據 |
| --- | --- |
| 來源 | 163 個 C/H；125 個 CODE、12 個 DATA 單元 |
| 編譯證據 | 保留父 544 物件證據與 2,197 個父輸入；另編譯 origin／src 的 C11／C++17 四物件；合計 274 組比較／548 物件，未宣稱重編全部 |
| 原位址 | 6,182 個 CODE owner、63 個 DATA OBJECT、41 個相鄰區段；5,270 個重定位角色完整保留 |
| 尚缺 | 3,290B：刻意排除 3,128B＋其他未選 162B；6 個 APP source provider 未解析 |

## 新增資料的使用證據

`0xCF5A` 的原始讀取公式為 `0x1A078 + 16*mode + ((fresh_record4+1)&15)`。依 [完整查表合約](../tsl9-third-provider-lookup-contract/README.md) 與 [寫入來源](../tsl9-mode-state-writer-contract/README.md)，mode 1／3 的條件讀取落在以下半開區間：

- mode 1：`[0x1A088, 0x1A098)`，16 bytes。
- mode 3：`[0x1A0A8, 0x1A0B8)`，16 bytes。

兩列均有真正的 C 常數陣列及正向 native OBJECT，並通過原廠資料比對；未建立完整 `1A078` provider alias。setter 接受任意 A0 低位元組，局部明確寫入值 1～5 不等於全域 mode 值域。間接呼叫、alias、排除 CODE、IRQ／DMA、初始化效果與寫入至讀取的一致性仍未知；不強制限縮 mode，也不宣稱每一欄實際可達。

既有全部 CODE／DATA owner 內容與座標、六個 import、六個 DATA label、CODE continuation 觀察均保留，包括 `0x8034→0x8038` 啟動邊界。未使用填零、padding、stub 或新增完整 provider 別名補缺口。

## 驗證與可刷寫門檻

有凍結的本機父產物與 LLVM 時，於 repo 根目錄執行：

```sh
python3 experiments/tsl9-record-mode-row-integration/audit-v1.py --tool-dir "$LLVM_BIN"
python3 experiments/tsl9-record-mode-row-integration/check-readiness-v1.py --tool-dir "$LLVM_BIN"
```

`LLVM_BIN` 是本機已配置的 LLVM 工具目錄。第一項檢查正式證據；第二項目前回傳 **exit 2**：證據核對成功，但韌體未就緒。exit 1 表示證據漂移或檢查失敗；不能忽略。八項門檻中僅來源／原生證據成立，APP 完整性、provider、可載入產物、原機 ROM／ABI、啟動／IRQ、RAM、Flash／OTA 與重建後功能證據仍不足。

診斷 ELF 為 entry 0、PT_LOAD 0，**不是可刷寫 BIN**。這輪未執行 target、HOST model、ISA 模擬、硬體或第三方 API。來源擴充前已重播父來源及 mode 使用證據；擴充後保留固定證據與所有相關輸入，僅以精確重建的舊 manifest 處理歷史快照差異。

[摘要](summary.json) · [完整收據](audit-result-v1.json) · [readiness 收據](readiness-v1.json) · [來源擴充](source-extension-v1.json) · [待實作功能構想](feature-candidates.json)
