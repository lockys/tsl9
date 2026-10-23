# 標記傳送路徑重建

[English](readme.en.md) · [C/C++ 原始碼](../../src/native/receive/tagged_dispatch.c) · [詳細流程與限制](../../experiments/tsl9-tagged-dispatch/README.md)

已將官方韌體 `0x16B7C–0x16C72` 的246 bytes／86條指令重建為 C/C++ 私有架構分區；涵蓋 tag 檢查、64B frame、記錄打包、busy 分支與狀態回傳。兩種語言的實際編譯、132項負向檢查及唯讀重播通過。11個控制重定位、4個外部提供者與 ROM 身分仍未解決；候選尚未加入既有1162-byte整合。

`src/` 已達61個C/H、35個原生單元、70組C/C++比較、140個物件；這些是靜態證據，**尚未完成逆向或產出可刷寫韌體**。

[摘要](summary.json) 區分已確認事項、推論與未知。[公開收據來源對應](publication-provenance.json) 保留兩份可攜原始收據的完整位元組，以及一份僅匿名化路徑的衍生檔；原始收據及失敗紀錄保留本機，不改寫 Git 歷史。既有816份匿名化衍生檔亦通過殘留欄位檢查。
