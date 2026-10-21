# 明確的 ABI 保存順序與可重驗物件轉換

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

此輪補齊兩個 C/C++ 函式的原始堆疊保存順序。工具與規則位於 [獨立模型](../../experiments/tsl9-v4160-frame-schedule/README.md)。最後產物明確包含編譯器輸出與 ABI 保存順序處理兩層，不宣稱是編譯器單獨生成，也不宣稱完整來源重建或可燒錄。

父層驗證對前一輪實際 C／C++ 編譯物件進行處理，兩者各只改變 14 bytes，並重讀輸入、輸出、metadata、符號與全部 RELA。每語言七個實際收據／輸出篡改案例均遭拒絕。此項驗證沒有重新編譯 C/C++，不代替新版完整映像的全新編譯鏈。

獨立 ABI 審查位於發佈後的 [frame-pass-review](../v4160-flash-register-prefix-2026-10-22/ABI-review/frame-pass-review/)。該審查另核對實際物件、原始保存指令、完整映像 witness link、進入點與畸形控制案例。個別收據所記錄的工具版本與輸入身分才是其權威；早期診斷收據不當作新版通過證據。

```sh
python3 -B analysis/v4160-frame-schedule-2026-10-22/implementation/check.py --project-root /absolute/project
```

預設檢查發佈的來源與封存證據身分，**不表示本機實際物件已重驗**。可加 `--actual-verification /absolute/project/path/verification.json`，明確讀取同專案內的實際物件與負例重驗。所有結果均不涵蓋未記錄的內部進入點、原機 ROM、實體中斷／故障或 BLE OTA。

獨立審查的 `build/` 編譯物件保留在本機交付目錄，不加入 GitHub；封存 seal 保持原樣。此處檢查器會明確列出缺少的封存成員數，不能把來源／metadata 核對稱為完整獨立成品重驗。需要完整封存重驗時，在包含全部成員的本機目錄執行該審查原有的 `check_seal.py`；新版完整映像另以當次實際編譯物件獨立核對。
