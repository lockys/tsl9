# 十一個可讀函式的完整映像來源規劃

[English](readme.en.md)

本規劃讀取前輪實際 `source-integrated.o`，並核對固定的配置清單與 34 個原始 C 載體。原廠初始載體有 8,280 筆 RELA；前輪 IRQ 來源整合後是 8,276 筆。本報告使用後者，不把它誤稱為未修改的原廠物件。

把五個 IRQ／RCC 與六個 Flash 函式合併列入來源取代範圍後，共有 11 個原始區段、526 bytes。691 個配置仍須完整保留，680 段是取代範圍外的儲存。四個原始 C 載體需要精確移除指定引號組語區塊；報告保留實際過濾後的雜湊，未改動原檔。預計原生編譯單元為 34 個載體、兩個 IRQ 可讀單元及六個 Flash 單元，共 42 個；這是規劃，還不是實際完整建置結果。

既有物件中，取代範圍外的 8,259 筆 RELA 必須保留完整角色與次數；範圍內有 17 筆呼叫／分支，須逐筆以真正的新來源重定位取代。20 筆範圍外引用都進入原始函式起點。六個 Flash 私有分支標籤的語義也要核對；不能只因為尺寸相同，就把舊的數值 interior alias 掛到新指令上。

program 的原始 100-byte 區段必須有完整來源。原區段末六個 bytes 是有效的 AND、store、return，不能當作 padding 或省略。新版若編譯成 100 bytes，也仍需檢查實際指令邊界、分支、符號與輸出暫存器。本規劃不替尚未完成的原生或完整映像契約放行。

```sh
python analysis/v4160-flash-entry-order-2026-10-22/image-plan/prepare_plan.py --project-root . --merged-object /absolute/path/to/source-integrated.o --check
```

實際物件必須符合報告中的固定雜湊。六個表格變異分別驗證：缺區段、豁免六個 bytes、把有效指令當 padding、遺失外部 RELA、捏造 interior entry、漏掉 incoming reference，都會拒絕。這些是來源規劃約束的測試，不是原始 CPU 或硬體執行。

此範圍沒有完整原生編譯、新 BIN、硬體或 OTA 結果。已記錄引用的完整核對也不能排除未知 ROM、數值間接引用或非同步中斷狀態。
