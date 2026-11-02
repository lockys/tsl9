# V4.1.60 候選映像來源建置

[English](readme.en.md)

執行 `python scripts/build-v4160-source-candidate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`，從 `src/` 與專案建置工具分別編譯 C 和 C++，各生成 76,800 bytes 的候選映像，並檢查其 SHA-256 是否等於既有 TX-integrated 候選。建置過程不讀取既有候選 BIN。

完整建置先檢查條件式連結：兩個符號有區段載體，三個資料符號使用條件式別名；嚴格連結仍缺少 `0x40000`。診斷連結使用數值位址見證，並與獨立組合的 BIN 逐位元組比較。這不證明 ROM、RAM 或索引假設。

`src/native/tx_candidate/full-image-payload.json` 保留既有候選映像的 3,128 bytes 原始內容作為對照。建置時 [入口與轉交 66 bytes](../../src/native/receive/ota_entry_14056.inc)、[結尾 14 bytes](../../src/native/receive/ota_epilogue_14098.inc)、[後續分支 54 bytes](../../src/native/receive/ota_more_140a6.inc)、[命令路徑 70 bytes](../../src/native/receive/ota_ae_140dc.inc)、[另一命令路徑 50 bytes](../../src/native/receive/ota_ad_1417a.inc)、[命令分流 90 bytes](../../src/native/receive/ota_dispatch_141d6.inc)及[分流續段 88 bytes](../../src/native/receive/ota_dispatch_14230.inc)由 C/C++ 架構指令編譯，取代對應載體；其餘 2,696 bytes 仍由原始資料載體提供。這些區段依賴原始控制流程與 stack frame，不能獨立呼叫。其他來源也可能包含原始指令或資料載體。此結果不代表完整原始碼還原、嚴格連結無依賴、實機啟動或功能經驗證。原有數值位址見證仍用於診斷布局。

**候選檔尚未驗證可安全燒錄。** 原機 ROM／ABI、RAM、IRQ、OTA 和實機功能仍須獨立確認。此建置不操作硬體。
