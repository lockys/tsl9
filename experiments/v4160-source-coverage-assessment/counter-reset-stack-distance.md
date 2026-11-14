# 條件式 reset SP 距離

`counter-reset-stack-distance.py` 依原 BIN `0x186b2` 的 AUIPC/ADDI 解得 reset 序列設定 SP 為 `0x20010000`，並核對兩個 callee 前綴。若入口 SP 等於該值減去非負、4-byte 對齊的深度，最近的 counter 別名分別是：

- `0x12506`：深度 48,956（`0xbf3c`）bytes。
- `0x175e8`：深度 48,964（`0xbf44`）bytes。

程式逐一檢查較小的對齊深度。這只是條件式數值比較，不是完整堆疊上限；其他 stack context、SP 重設、中斷、provider 及可達性都未證明。

## 參考 resident 線索

本機 WCH SDK 候選 V1.31 的 `0x40138`、`0x4013c` 指向 `0x4cfd0`、`0x4b456`；V1.40 對應 `0x4d068`、`0x4b4ee`。候選映像雜湊與候選語意分別見 `analysis/wch-resident-candidate-2026-10-21/` 及 `analysis/boot2580-w-provider-offline/README.md`。SDK 將兩槽稱為 `GATTServApp_InitCharCfg` 和 `GATTServApp_ReadCharCfg`；這是參考資料而非 TSL9 實際安裝 ROM 的證據，不能直接推論實際寫入長度。
