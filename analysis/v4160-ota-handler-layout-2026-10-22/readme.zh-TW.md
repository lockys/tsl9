# OTA 元件的真實 provider、指標與 BOOT 範圍

[English](readme.en.md)

本輪將現有 568-byte C11／C++17 元件與實際完整映像的 provider 物件做 `ld.lld -r` 部分連結：**九個外部參照均綁定到真實配置區段，只剩原有 `__tsl9v4160_rom_entry` 為 UND**。這是 provider 接合證據；**原 caller 仍呼叫原 530-byte 本體，新 C 函式尚未接線，沒有 final ELF 或新 BIN。**

## 部分連結的實際結果

兩種語言各使用既有、由原 receipt 核對過的 `source-integrated.o` 與 `ota_handler.o`，不重新編譯已封存程式。輸出為真正 ET_REL：692 個非空配置（原691加新568-byte section），8,281 筆 RELA（原8,261加新20）。所有原配置 bytes 及重定位語義保留，原 raw handler 與新 FUNC568 同時存在。provider 不是數值 ABS、stub 或偽造 FUNC，ROM 未解析狀態也沒有用忽略 undefined 選項隱藏。

`-r` 不代表最終 JAL 已套用或範圍已核對，也沒有更動原 caller 的目標、驗證 installed ROM 或准入硬體。詳見[部分連結工具與唯讀重驗](provider-link/README.md)。現有共享 C/C++ 仍在[原模型](../../experiments/tsl9-v4160-ota-handler-compact/README.md)，獨立元件仍為568 bytes，原位仍差38 bytes。

## 回覆指標的實際逃逸

S 的兩-byte 回覆先經 `0x13E98`，進入共用封包組裝 `0x13B4C`。組裝函式先把來源 pointer／length 存入 live frame，且在配置類 slot `+0x70` 呼叫前，A2 仍帶原 pointer；之後才將重讀的 pointer 傳到 fresh copy slot `+0x4C` 的 A1。因此僅證明兩份 copy 候選不比較特定 stack 範圍，仍不足以宣稱數值地址無關。

新 private reply 在 SP+6／7，SP+12 已保存 S7，不可直接綁回原位置。內容投影還需要 slot70 不觀察／保留 ambient pointer、copy 為已安裝實作、有效 RAM／無不當 alias 或非同步觀察，以及後續 TX／release 等契約。這輪核對 546 bytes／209 個原始指令欄位與五個 operand 反例，沒有把這些條件變成全域 ABI 通過。見[consumer 與條件清單](reply-review/README.md)。

## BOOT 的數值頁範圍

實際讀取選定 BOOT ID2580 的414-byte／144指令命令本體與4-byte排程跳轉，原 unsigned guard 允許頁0..95，目的地為 `0x08008000 + page*1024`，最後完整頁結束於 `0x08020000`。目前 Runtime 為76,800 bytes／75頁、數值 EOF `0x1AC00`。後續21頁／21,504 bytes只是這份候選 guard 的數值餘量，**不是 free Flash、NV 區所有權、實體容量、已安裝 BOOT 或 updater 接受證據**。

此有界本體未提供 whole-image CRC／完整性完成檢查證據；不能推廣為整條更新流程沒有驗證。詳見[原始位元欄位、邊界與五個反例](boot-review/README.md)。值得加入的功能提案是離線更新檔分區預檢，區分 BOOT／Runtime 與候選頁上限，並顯示仍未知的裝置身分；未當成已交付硬體功能。

## 沒有採用的派送改寫

一次完整32位命令的 C `switch` 探針在 C11／C++17 都產出與568-byte基線逐 byte 相同的193指令，不推廣新模型，不搜索 compiler flags。原工作區保留實際 object／IR／MD／receipt；發布只含來源與有界中繼證據，預設不聲稱已重播未交付的 archive。見[探針與明示實檔重驗](dispatch-probe/README.md)。

## 邊界與後續

完整 TX 實驗 BIN 仍為 SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`，十三個原始範圍共930 bytes由可讀 C/C++ 與明示 ABI 層提供，其餘原始承載仍保留。本輪部分物件的新568 bytes沒有加進完整 BIN 或功能完成率。

下一個關鍵 provider 問題是 slot70 的 ambient A2／frame footprint；配置則需原 caller／continuation、Flash／NV／初始化資料、相對分支及更新封裝證據。可以研究合法的非原位配置，但不可只因候選 guard 容許頁75就把該空間當作可用。完整硬體、ROM／BOOT、RAM／IRQ、Flash、BLE OTA 接受與復原仍未證明。[本輪計畫](plan.zh-TW.md)保留完整目標。

全程僅靜態讀取、C 派送探針編譯及部分連結；沒有執行／模擬 RV32、操作硬體、呼叫供應商 API 或傳送 UID／VIN。交付／發布驗證不重編譯原568-byte程式或重跑未變 HOST 測試；Windows 實證也不代表 Linux／macOS 已驗證。
