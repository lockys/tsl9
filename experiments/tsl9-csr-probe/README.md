# 核心識別診斷元件：不可刷寫

[English](readme.en.md)

此實驗函式嘗試讀取 `marchid`、`mimpid`，再向呼叫端提供的同步 callback 傳送 12-byte 資料：`T9D`、版本 1、兩個小端序 32-bit 數值。不讀取 UID、VIN、MAC 或周邊 MMIO。callback 必須在返回前複製資料；函式返回後 stack 緩衝區即失效。

[WCH 青稞 V4 手冊](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf)將這兩個 CSR 列為 machine mode 唯讀；這不能證明原機核心、呼叫權限或讀到的值，也無法單憑它們確認完整 MCU 型號。

**編譯產物只有函式機器碼，沒有開機入口、BLE 傳輸或 OTA 韌體結構，不能刷寫或獨立運作。** 原機插入位置、記憶體、呼叫與通知契約尚未確認；未連接現有 app，也沒有實機資料。C 與 C++ 編譯結果相同屬離線證據，非設備驗證。

本機試驗產物 `NOT-FLASHABLE-diagnostic-component.bin` 為 90 bytes，SHA-256 為 `52a636714bf33832c99b2883e76e16d3380cef5ad66580fa700ef98e356c8cd2`。若未來以已驗證方式取得單筆 12-byte 原始紀錄，可執行 `python experiments/tsl9-csr-probe/decode_probe.py record.bin` 離線解讀；這不是硬體紀錄擷取功能。
