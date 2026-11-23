# v4.1.60 佇列的零 ID 槽位

原始 BIN SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。離線指令顯示 `0x12bc8` 掃描 32 個、每個 12 bytes 的槽位，尋找首 halfword 為零者；找到後寫入 ID 低 16 位和 `+2` 的低 byte，呼叫 `0x4004c` 所指的未知函式，再寫 `+11`。沒有看到對輸入 ID 零的拒絕。

在該函式正常返回、provider 不改 ID 且沒有其他寫入的條件下，寫入 ID 零後槽位仍以零標記；`0x12c58` 的消費迴圈在 `0x12c94` 跳過它，後續 producer 可重新選用該槽。這不是覆寫非零 ID 的已佔用槽。間接 provider 的實作、實際長度、副作用及中斷競爭均未知；消費端先測試 ID 才操作 CSR，不能由此宣稱原子性或實機結果。

本機 `analysis/check_v4160_zero_id_queue.py` 固定 producer/consumer 的部分原指令，並在假設 provider 精確複製一 byte 的合成模型中檢查 32 個槽位的跳過與重用；普通和 `-O` 通過。此為手寫模型，並非 CPU 執行或硬體證據；腳本尚未發布。
