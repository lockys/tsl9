# 任務 ID 7 如何走到 selector 5

接續 0x6dd2e 的兩分支：空回呼表註冊成功與 12 格全滿的對照。每組從 0x45220 入口接續實際模擬的暫存器與 RAM，不重設 SP、返回位址、保存的 ID、回呼表或 I/O 樣本。

四個入口 0x45220、0x48c56、0x47eac、0x6d682 各自返回到 0x4657a、0x4657e、0x46582、0x46586；各有 75、14、11、20 次寫入。以 0x46570 入口 SP 為 S，四個呼叫均未覆寫 [S−20,S−16) 的 ID。0x4659c 從該處重讀 7，0x465a8 寫低 byte 至 0x200033ac，0x4da0c 再寫至 0x2000332e，0x4da0e 寫 selector 半字 5 至 0x2000332c。返回 0x6dd3e 時 a0 為 0，非 ID。

64 組各自成對，共 128 次延續；沿途未寫入 48-byte 回呼表，兩表內容仍不同。一般與 -O 均通過：`PASS: 64 initializer pairs to 6dd3e; live saved ID 7 -> 200033ac and 2000332e; selector 5; distinct tables unchanged`。另有 1024 組既有獨立起始條件的回歸通過。

限 V1.31 參考 resident、Xwchc 解讀及合成記憶體、外設成功存取；未連接裝置，未執行事件派送。不代表所有裝置或任意回呼表配置。
