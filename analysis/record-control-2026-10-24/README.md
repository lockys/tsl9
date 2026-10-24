# 記錄處理與事件啟動

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/record_control.c)：原廠 `1798A–179FC` 共 **114B／44 指令／12 架構區塊**。C11／C++17 皆通過98個非控制bytes與6個具型別控制參照的完整核對；純資料原位址編碼後全114B與原BIN相同。[證據](evidence/standalone-trial.json)

## 已確認的靜態行為

- `1798E` 以unsigned比較限制A1<=35；超出時在配置frame前返回。
- 零模式路徑使用32B frame，傳遞來源 `word[GP+100]+7*A1`、目的 `SP+8`、長度7給間接表項 `4004C`。這是參數與存取順序證據，不保證已安裝callee的身分。
- `179B2` 讀取完整SP+8 word，擷取bits10..15。mask bit0／bit1分別允許更新GP+367／368；值取自各次fresh SP+12 word的bit23。
- `179D8` 將SP+8傳給真實未解析提供者 `1787C`，再走32B frame的共用還原出口。
- 非零模式在 `179E4` 將低A1存入GP+376，以GP+379、事件值2及時間參數2呼叫表項 `40058`，然後共用還原出口。未推定實際經過時間或裝置動作。

**7B參數不代表可以縮窄原碼讀取。** SP+12的完整word包含複製視窗外的SP+15，原full-word存取已保留；沒有加入初始化或改成byte讀取。GP欄位也未擅自命名為座椅或免打擾設定。

## 真實整合與限制

原初始化鏈的 `1798A` 參照已綁到8B真實入口，完整114B一起連結。新元件為 **2730B code＋456B data，256個非零FUNC、10個入口alias、231 RELA、17個直接UND**。前一階段2616B code／456B data及62個非零向量綁定全部保留。解決1798A並引入1787C，所以UND數沒有下降。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

SDK預設表項與memcpy／start-task配置對應，但表項位址不是函式入口，也不證明installed ROM或callee ABI。[對照](rom-profile-correspondence.json)

`src/`目前88個C/H；code來源比對122組／244物件，指標資料另2組／4物件，共 **124組／248物件**。來源比對與原始指令吻合不證明整體行為；仍是VMA0 ET_REL，原機硬體、ROM、記憶體、完整啟動／IRQ及BLE OTA均未通過。

## 後續與功能候選

[下一組有界反組譯](next-1787c-frontier.json)保留完整1787C–1798A的270B，包含1787C／178F8／17948入口候選；第一段有16槽／7B記錄佇列特徵與往17666的尾跳，須繼續驗證callback與private register契約。後續可探索離線7B記錄檢視器，先顯示原始遮罩、索引與事件參照；尚未實作，未確認語意的欄位不給功能名稱。

本輪無目標／HOST model／ISA執行、硬體或網路操作，沒有新BIN、commit或push。[建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
