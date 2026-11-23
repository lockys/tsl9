# v4.1.60 零 ID 佇列指令執行驗證

離線使用原始映像 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，以受限 RV32IMC 解譯器執行 producer 的實際指令，並檢查 consumer 的 ID 分支。32 個前方已佔用槽位數案例均檢查零 ID 寫入、consumer 跳過、同槽非零 ID 重用；另測全滿佇列及反轉分支指令的負向控制。一般及 Python `-O` 直接執行均通過。

限制：provider `0x4004c` 以假設只複製一 byte、正常返回且保留其他暫存器的 stub 替代；consumer 僅執行至 ID 分支後，槽位 1–31 從 guard 直接進入，不模擬前面已佔用槽的完整處理。這不是設備模擬，也不證實際中斷、provider、零 ID 可達性或硬體結果。驗證腳本 `analysis/test_v4160_zero_id_queue_cpu.py` 目前僅本機。
