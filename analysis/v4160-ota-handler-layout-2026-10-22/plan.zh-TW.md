# OTA 元件的 provider 與配置證據計畫

[English](plan.en.md)

完整目標仍為可由原藍牙 OTA 寫入原硬體的 C/C++ 重建 BIN；這輪不把部分連結、數值範圍或候選 ROM 當作相容性准入。

1. 以 `e2369bd` 的 568-byte 元件與實際 D／P 產物為基線。只探測一次完整32位命令的 C `switch` 派送；若機器碼相同則保留否定證據，不推廣新模型或搜尋編譯旗標。
2. 追查 S 回覆的實際 consumer：wrapper、共用封包組裝、配置／複製 slot、既有 TX。辨識數值指標是否跨越 opaque 邊界，將「只觀察兩-byte 內容」的必要條件列明，不能因候選 copy leaf 簡單就忽略其他 callee、alias 或非同步觀察。
3. 重新讀取選定 BOOT ID2580 的原始命令本體與最小排程跳轉。以實際 unsigned guard、頁碼與目的地運算核對 Runtime 頁範圍，將後續數值頁數與 free Flash、已安裝 BOOT、NV 區及 OTA 接受明確區分。
4. 以現有真實 `source-integrated.o` 和 568-byte native object 執行 pinned `ld.lld -r`。核對所有原始配置 bytes／重定位語義、九個真實 provider、仍未解析的 ROM 入口及原始 caller。保留原 530-byte 本體及新 C 函式；不重導入口、不用 ABS／stub／defsym／忽略 undefined 參數湊成功。
5. 預設只查 metadata；明示 actual 路徑才讀原 BOOT／Runtime、既有 native／ELF／候選來源，或建立新部分連結。所有 actual receipt 都必須可唯讀重驗；先修正尚未發布的驗證器錯誤，再封存同一個平面 CLI，不增加包裝層掩蓋問題。
6. 交付後在 `re-tsl9` 與發布副本重新執行相應 actual 檢查／部分連結，保護既有檔案，於已授權私有 GitHub 提交里程碑。本輪不重編譯已封存 568-byte 元件或重跑未變的 HOST 測試。

`-r` 不代表 final relocation／JAL 範圍已完成，也不使原 caller 改呼叫新 C。原位大小仍差38 bytes，但「必須剛好530 bytes」不是所有合法配置的必要條件。後續需以真實 provider、存活來向／continuation、可觀察 ABI、Flash／NV／初始化版面與更新格式證據選擇配置；不得用未證明的空間或原始 bytes 補缺。

本輪沒有 final ELF、新 BIN、目標執行／模擬、硬體操作或供應商 API。完整硬體／ROM／BOOT／RAM／IRQ／Flash／OTA 接受及復原仍未完成。
