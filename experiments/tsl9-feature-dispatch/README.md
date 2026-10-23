# 完整功能分派器的有限靜態重建

[English](readme.en.md)

本輪以三個 C 單元重建完整 `14D2E–154A6`（1912B），另包含 `829E–82A8` 模式 getter（10B）及兩張 signed-relative 跳表（60B）。同一份來源已實際編譯為 C11／C++17。210個 FUNC 是架構區段，不代表210個一般 C ABI 函式。

| 檢查範圍 | 實際結果 |
| --- | --- |
| 新程式與表 | 1922B code／669指令／60B table |
| 重定位 | 208個直接控制、4個PC-relative及30個table relocation |
| 原位址驗算 | 純資料重定位編碼後，全部新code／table位元組與官方BIN相同 |
| 接入既有元件 | 5088B code＋60B table、401 FUNC、386 pending RELA、70個真正直接 UND |
| src整理 | 74個C/H、48個native units；96組比較／192物件；舊90組及541個artifact記錄未變 |

沒有提供假的 ABS 函式或把70個下游實作視為已完成。輸出的 `ET_REL` 是未解析的診斷物件；`ld -r` 將 section VMA 保持為0，檔名的 ORIGINAL-ADDRESS 只是原位址對照契約。它沒有可執行的載入配置，不能當作可刷寫 BIN。

C擁有一般記憶體、GP欄位、常數及位元運算；保留的S0／SP／RA、部分S0相對讀取、控制與PC效果是明確架構介面。固定LLVM拒絕直接把S0當C輸出變數的失敗試驗完整保留。沒有假設呼叫後的SP／S0或原始封包一定保持。

## 驗證與保留範圍

最新 `verify-v2.py` 對正常實際編譯產物核對來源、依賴、工具、完整符號角色、唯一名稱、global ABS限制、所有配置區段、真實相對表及原始位元組。父元件採「舊manifest只增加三組精確來源資料」的範圍重驗；未冒稱原始全域收據在新manifest下原樣重播。

v1程式與兩語言各10173個歷史負例收據保持原樣。獨立覆核發現其同名符號角色檢查不足，v2加入嚴格唯一性／角色／ABS檢查及父proof資料釘選；目前正常產物通過。後續獨立畸形輸入覆核回合遭安全檢查中止，未改道重試；v2沒有執行新的負例矩陣，歷史數量不能證明新增檢查。

本機保留的graph-v2與原始輸入可作唯讀核對：

```sh
python3 scripts/verify-curated-source.py --replay build/curated-source/feature-dispatch-20261023-v2/verification.json
python3 experiments/tsl9-feature-dispatch/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-feature-dispatch/build/graph-v2/c --mode c
python3 experiments/tsl9-feature-dispatch/verify-v2.py --tool-dir "$LLVM_BIN" --folder experiments/tsl9-feature-dispatch/build/graph-v2/cpp --mode cpp
```

以上完整重驗需要本機保留的原始建置／父元件收據；公開路徑匿名化副本不能取代原始重播輸入。Windows固定工具鏈已測試，其他平台尚未建立相同證據。一般來源編譯可用 `scripts/verify-curated-source.py --tool-dir "$LLVM_BIN"`；不下載工具、不執行target／HOST模型／ISA／硬體／網路API。

## 尚未閉合

兩處PC算出的 `1069E` 是真實callback，交由1083C間接呼叫；非零路徑還會向9124註冊107C0，並涉及其他resident。它不是70個直接UND可完整描述的範圍。見[callback證據](../../analysis/feature-dispatch-2026-10-23/callback-frontier.json)。

installed ROM、實體MCU／控制器、完整啟動／記憶體／IRQ／clock、Flash與OTA仍未證明。本輪沒有產生或刷寫新BIN。值得新增的功能仍為純離線濾波／路由請求檢視器，尚未實作，不能把設定例程當作唯讀硬體診斷。
