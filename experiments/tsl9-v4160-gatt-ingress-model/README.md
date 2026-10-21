# V4.1.60 GATT 接收與跨回呼解析

原 ID2966 的 `888C..8A56` 共458 bytes，重建為可讀 C11/C++17 語義模型。這是自訂 host API，並非宣稱已知原 callback C ABI。數值記憶體、81B0 clock helper、CCC slot與14056整個router都經顯式 provider；沒有真實通訊、硬體driver或可燒錄映像。

解析狀態共用 GP-relative memory，不按 connection 分流。片段可跨回呼延續；router取得的是收到 checksum 時那次呼叫的 context。固定 payload buffer 是 `0x2000B9D8`。模型保留 live read/write 順序、checksum modulo256、長度上限1040、payload counter上限1039，以及錯誤時只清state、不重試當前byte。attr.value與incoming offset不在普通路徑驗證；不能替原程式加上不存在的條件。

時計 helper 的返回值不等於已知硬體毫秒；原判斷為 uint32(now-last)>299。零長度chunk仍會更新時間。原 loop以low16(index)比較完整a3；模型不捏造n<=65535檢查。`max_operations`是明示的觀察預算，耗盡時保留先前效果並回 `GI_OBSERVATION_LIMIT`，不是原機拒絕或成功。

一般返回0、permissions bit32返回8，CCC tail返回保留provider的未知結果。HALT/TRANSFER不撤銷先前效果。未知值導致無法決定的條件會停在明確證據邊界，不轉為有效封包或完整功能。

```powershell
.\verify.ps1
.\verify.ps1 -Cpp
```

先核原BIN與source-map，再以MSVC `/W4 /WX`執行合成記憶體測試。測試資料使用合成bytes與合成router provider，不含UID/VIN或對外傳送器；沒有判定測試命令在真實router中的功能。測試不證明resident註冊、實體BLE接收、ROM/IRQ/stack或更新相容性。
