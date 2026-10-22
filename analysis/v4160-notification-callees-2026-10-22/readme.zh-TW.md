# 通知 helper 的一段有界候選證據

[English](readme.en.md)

這是 OTA handler 工作開始前保留的旁支調查，只讀本機兩份官方 ROM 候選。V1.40 `0x45228..0x4525E` 與 V1.31 `0x45194..0x451CA` 都是54B／22條指令的 wrapper，包含一個可選的 RAM helper 及尾端委派。它們不是已安裝 TSL9 ROM 的量測。

可選的56B RAM helper 已有界核對；尾端 `0x44866`／`0x447D2` 沒有閉合，因此不宣稱完整 transitive ABI。來源中的 builder 位址以 LUI 加 signed ADDI 正確計算為 `0x44E44`／`0x44DB0`。細節、profile 條件、raw-field 反例及明示本機來源核對入口見 [candidate-review](candidate-review/README.md)。

本輪沒有另建 ROM C 模型或將 vendor ROM 打包入韌體。主要程式工作轉為[原 App OTA 命令本體](../v4160-ota-handler-2026-10-22/README.md)，不以繼續遍歷整份候選 ROM 取代 App C/C++ 重建。沒有執行／模擬目標、下載或操作硬體。
