# WCH 官方 BLE V1.40 來源核對

[English](readme.en.md)

WCH 官方 CH32V20x 專案在 commit `b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1` 的 [wchble_rom.hex](https://github.com/openwch/ch32v20x/blob/b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1/EVT/EXAM/BLE/LIB/wchble_rom.hex) SHA-256 為 `5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23`，與本機先前用於跨版分析的 V1.40 候選 HEX 完全相同。[官方標頭](https://github.com/openwch/ch32v20x/blob/b375bbbc7dfe8642d6fb7c17e6d3207ee1c3c9c1/EVT/EXAM/BLE/LIB/wchble_rom.h)標示 V1.40、版本字串 V1.4；本次取得標頭的 SHA-256 是 `fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e`。

本地[版本檢查器](../tsl9-six-dependency-ledger/check-gatt-resident-versions.py)以此官方 HEX 及既有 V1.31 檔核對，結果通過：V1.40 版本字串與 TSL9 APP 的 21-byte V1.3 前綴不相同；V1.31 前綴相符。只有當實機載入的比較函式、呼叫約定與候選相同且呼叫正常執行，才能套用既有的版本守衛推論。此核對證實參考檔來源，不確認實機 resident、啟動成功或相容性；不要燒錄候選 HEX。

進一步由 WCH 官方 GitHub 的[舊版固定 commit](https://github.com/openwch/ch32v20x/blob/ec059e0b18046b111ee850e44f105fcd095e775c/EVT/EXAM/BLE/LIB/wchble_rom.hex)取得公開 HEX，SHA-256 為 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5`，與既有本機 V1.31 候選逐檔雜湊相同。使用這兩份官方 HEX 重跑版本及槽位檢查通過。V1.31 的前綴相符是候選啟動條件的必要線索，並非實機版本、完整 ABI 或可燒錄性證明；不可把它視為實機備份。

驗證只讀取允許的 APP 版本字串與公開 HEX，沒有讀取 APP 排除區、連接硬體或執行 target。

兩版官方候選 HEX 的 TX 相關跳表指標也已核對：`0x40050` 在 V1.31 指向 `0x4354A`、V1.40 指向 `0x435D6`；`0x4013C` 分別指向 `0x4B456`、`0x4B4EE`。V1.40 官方標頭將這兩槽分別宣告為 `tmos_set_event` 與 `GATTServApp_ReadCharCfg`，與既有 V1.30 標頭的槽號及函式簽章一致。不同實作位址顯示不能把一版的內部位址硬編碼到另一版；兩個槽值與宣告一致本身仍未證明函式行為相同、實機載入哪個版本或候選程式可啟動。[檢查器](../tsl9-six-dependency-ledger/check-gatt-resident-versions.py)已固定兩版的槽值。
