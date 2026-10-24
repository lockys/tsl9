# 輸出依賴與延後旗標

[English](readme.en.md)

本輪補上十個完整函式，374B／130 指令；C11、C++17 物件相同。主元件接通六個舊入口，沒有新增依賴，剩餘提供者從 179 降至 173。原生連結器配置後，34,548B code／data 逐 byte 與官方 BIN 相同。**產物仍是 entry=0、PT_LOAD=0 的診斷 ELF，不是可刷韌體。**

| 原始入口 | 已確認的靜態行為 |
| --- | --- |
| `8E6A`、`F84A` | ROM 槽位 `0x40058`／`0x40048` 的原始參數與尾轉移 |
| `9F7A`、`9FC8` | 清除旗標、條件排程、回呼時重新讀取設定與旗標 |
| `D7D4`、`D810` | 記錄欄位處理、同一指標兩次呼叫、狀態分派與清除 |
| `F818`、`F822`、`F82C`、`F838` | 四個 RAM byte 寫入、讀取或複製入口 |

`9FC8` 排程數值為 10000，時間單位仍未知。`9F7A` 保留 `(旗標 XOR 1) & 1`，不能簡化成布林反相，也不能使用排程當時的快照代替回呼時重讀。

`D7D4` 保留 signed byte 載入與 OR 操作，再把同一個堆疊記錄指標交給 `12A08` 兩次；第一次呼叫是否改寫內容尚未確認，因此不宣稱兩次 payload 相同。`D810` 保留 1–19、24、25、26 的原始分派與後續清除順序。產品功能名稱未證明。

[原始指令](evidence.json)、[83 個語意核對點](provider-contracts.json)、[結果與收據雜湊](summary.json)、[剩餘依賴](next-providers.json)、[唯讀診斷候選](feature-candidates.json)。候選功能著重於解釋旗標清除／延後更新原因及記錄提交來源，尚未接入硬體。

124 個 C/H 檔通過 196 組比較／392 個物件；舊 123 檔不變。流程核對涵蓋 11,478 指令、1,922 直接轉移，沒有一般續行缺口；1,709 個轉移目標已有實作，其餘 213 個仍只引用原位址。間接目標、IRQ 返回、EBREAK／向量邊界及實際可達性仍未證明。

從 repository 根目錄執行唯讀檢查：

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-output-dependencies/derive-v1.py --counts
```

編譯工具與標頭雜湊固定於 `spec-v1.json`。指定符合配方的既有 `LLVM_BIN`，可用 `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>` 建立新試驗；完整整合重播需要本機歷次收據。本輪無目標／HOST／ISA 執行、硬體操作或新增 BIN。實體晶片、ROM／RAM／IRQ、啟動與原 OTA 相容性仍未通過。
