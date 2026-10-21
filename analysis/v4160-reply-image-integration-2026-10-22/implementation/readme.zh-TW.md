# 十二個可讀函式的完整來源映像

[English](readme.en.md)

本範圍實際重新編譯34個原始載體與9個型別化來源單元，產生包含12個可讀函式／650 bytes的完整76800-byte離線映像。原本NOTYPE0／區域入口0保留在回覆區段的零長度來源邊界；新FUNC124獨立存在，未偽造原符號型別或ABS提供者。

`verify_image.py`是正式編譯、連結及唯讀重驗入口。`reply.o`先經明確`reply-order.json`步驟成為`reply-ordered.o`，再與其他型別化輸出合併。`canonical53.ld`把回覆的獨立輸入區段加入原本擁有者。`pre-frame-integrated.o`因此已含排序後回覆，不稱為純編譯器輸出；既有框架排序再產生`source-integrated.o`。兩步分別改動28與14 bytes，均只重排新編譯出的指令。

實際C11／C++17輸出的`NOT-FLASH-VALIDATED-reply-integrated.bin`皆為76800 bytes，SHA256為`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，與原版及前一個十一函式完整映像均為0差異。沒有用原始BIN、舊物件、填補或指令模板生成程式碼。

## 指令

```sh
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --tool-dir "$LLVM" --language both
python -B experiments/tsl9-v4160-reply-image-integration/verify.py --project-root . --replay RECEIPT
python -B analysis/v4160-reply-image-integration-2026-10-22/implementation/check_image.py --project-root .
```

工作區將`analysis/`改成`apk-analysis/tsl9-`。預設`check_image.py`僅核對封存與中繼資料；`--require-local-builds`要求兩份選定實際建置，`--receipt FRESH`可重驗其他新根目錄的實際收據。正式CLI另支援`--firmware`與編譯工具／建立新目錄覆寫，重讀時禁止工具／建立目錄覆寫。Shell入口提供相同參數。

實際每種語言為61個按順序核對的命令、43份完整`-MD`相依檔、74個專案輸入、14個產生輸入及1個實際Clang資源標頭。14個來源單元包含該資源標頭。來源、標頭、工具、證據與排序規則在使用前後核對雜湊；9份IR仍對應各型別化來源單元。

區段／符號／重定位檢查保留691個配置、679個載體及8257筆外部RELA，另有12筆型別化JAL，共8269筆。53個正規相對綁定、21個入口與11個原私有分支均有明確角色。實際`9DF4`的2-byte C.JAL連結為`9DF6`，未依RVC_JUMP重定位名稱誤判為無連結跳躍。排除型`.llvm_addrsig`明確核對56+1 bytes及新符號索引來源，最終ELF不包含它。

15個LOAD的位元組、記憶體與權限覆蓋全部原配置；匯出無洞、隱藏補位、RAM或ROM內容。缺少駐留ROM的嚴格連結拒絕；成功見證只設定數值0x40000。原本TX函式內容由保留來源載體實際提供。

每種語言41個實際反例皆拒絕：30個ELF／RELA／映像、4個相依檔、6個排序JSON、1個命令順序。另有5個唯讀CLI案例。選定收據中繼資料位於`receipts/`；`results.json`記錄實際W建置路徑及雜湊。物件、日誌與反例保留在本機忽略的`build/`，不隨中繼資料發布。

這仍是部分可讀重建加原始載體。未知駐留ABI、任意callee破壞SP／GPR、非同步／fault、計算出的內部入口、硬體、BLE／Flash／OTA相容性均未證明。沒有執行RV32、ISA模擬、網路、封包或裝置操作。目前工具證據來自Windows NDK27.1.12297006，未宣稱其他主機平台實測成功。
