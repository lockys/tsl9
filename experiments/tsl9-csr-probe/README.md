# 核心識別診斷元件：不可刷寫

[English](readme.en.md)

此實驗函式嘗試讀取 `marchid`、`mimpid`，再向呼叫端提供的同步 callback 傳送 12-byte 資料：`T9D`、版本 1、兩個小端序 32-bit 數值。不讀取 UID、VIN、MAC 或周邊 MMIO。callback 必須在返回前複製資料；函式返回後 stack 緩衝區即失效。

[WCH 青稞 V4 手冊](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf)將這兩個 CSR 列為 machine mode 唯讀；這不能證明原機核心、呼叫權限或讀到的值，也無法單憑它們確認完整 MCU 型號。

**編譯產物只有函式機器碼，沒有開機入口、BLE 傳輸或 OTA 韌體結構，不能刷寫或獨立運作。** 原機插入位置、記憶體、呼叫與通知契約尚未確認；未連接現有 app，也沒有實機資料。C 與 C++ 編譯結果相同屬離線證據，非設備驗證。

本機試驗產物 `NOT-FLASHABLE-diagnostic-component.bin` 為 90 bytes，SHA-256 為 `52a636714bf33832c99b2883e76e16d3380cef5ad66580fa700ef98e356c8cd2`。若未來以已驗證方式取得單筆 12-byte 原始紀錄，可執行 `python experiments/tsl9-csr-probe/decode_probe.py record.bin` 離線解讀；這不是硬體紀錄擷取功能。

`diagnostic_transport.c` 是獨立的候選介面：由呼叫端提供傳送函式、連線值與命令值，按原 `0x8A56` 所觀察的四個參數順序送出同一筆資料。此介面沒有指定命令，也沒有插入原韌體；只有當實機介面、記憶體與保存暫存器契約符合且傳送函式返回前完成複製，stack 上的資料才可安全使用。原始檢查有連線與其他守衛，呼叫不保證實際通知。這是離線組件，不是可刷寫 firmware。

`NOT-FLASHABLE-transport-component.bin` 是此介面的 110-byte 裸函式，C／C++ 離線編譯一致，SHA-256 `7d7eeaf1e1c7dd3d6d3d2a4e234529bd198e9017bf61ec5b1cbfa216c09a2eec`。反組譯核對了兩個 CSR 讀取及四個呼叫參數；沒有測試原機、實際 BLE 通知、App 接收或 OTA。**不可刷寫。**

原 reset 的 `0x1870C` 以 `0x1888` OR `mstatus`，會把 MPP bits 12:11 設成 3；[WCH 青稞 V4 手冊](https://www.wch.cn/uploads/file/20220411/1649641123177990.pdf)說明 MRET 時 MPP=3 保留 machine mode。若候選 resident 相符、啟動與 MRET 正常且期間 MPP 未被改寫，這支持 APP 入口處具備該 CSR 權限；不能保證之後的呼叫點仍處於 machine mode，也不能確認實機值。
