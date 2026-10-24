# 輸出組裝與比較函式

[English](readme.en.md)

本輪重建六個完整原始函式，956B／298 指令；C11、C++17 的物件相同。整合後 34,174B code／data 經原生連結器配置到原始位址，逐 byte 與官方 BIN 相同；仍有 179 個提供者未實作。診斷 ELF 的 entry=0、PT_LOAD=0，**不是可刷韌體**。

| 原始位址 | 已確認的靜態行為 |
| --- | --- |
| `9AE4–9AF0` | 向 `0x40010814` 寫入 32 位元數值 2；實體腳位未證 |
| `B6F4–B730` | 低 byte 篩選、完整 32 位比較與控制呼叫 |
| `DEA0–DEE2` | 狀態門控、保存 byte、後續呼叫與尾跳 |
| `17C4E–17CB2` | 組裝 `0x04F3` 記錄，交給 `12A08` |
| `17CB2–17CF4` | 保留無號差值與方向判斷，清除旗標或累積遮罩 |
| `17CF4–17F80` | 兩組記錄、八組比較、16 位元倒數與取消回呼 |

記錄有四個欄位 byte 未在本函式內賦值，另有讀取舊堆疊後才覆寫的指令，均照原碼保留。比較器使用 `uint32(A5-A6+5)<=10`；倒數沒有先判零，減一後以 16 位元截斷。產品功能名稱、時間單位、並行狀態、私有 ABI 與硬體行為仍待證明。

[原始指令](evidence.json)、[101 個語意核對點與八組參數](provider-contracts.json)、[完整結果與收據雜湊](summary.json)、[未完成依賴](next-providers.json)、[唯讀診斷候選](feature-candidates.json)。本輪接上四個舊入口，新增 `9FC8`、`D810` 兩個依賴；下一輪優先追查這兩者及高引用的 `8E6A`。

完整來源共 123 個 C/H 檔；194 組比較／388 個物件通過，舊 122 檔保持不變。流程核對 11,348 指令、1,899 直接轉移，未發現一般續行缺口；間接呼叫、中斷返回及 EBREAK／向量邊界的執行行為仍未證明。

從 repository 根目錄可執行以下唯讀檢查：

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-output-builder/derive-v1.py --counts
```

編譯配方在 `spec-v1.json` 固定工具與標頭雜湊。指定既有工具目錄 `LLVM_BIN` 後，可用全新的試驗名稱執行 `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>`；完整整合重播另外需要本機產生的歷次收據。本輪沒有執行韌體、HOST 模型、ISA 模擬或硬體操作，沒有新增 BIN；原晶片、啟動／ROM／RAM／IRQ 與 OTA 相容性仍未通過。
