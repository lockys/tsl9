# 命令分流續段的 C 行為模型

[模型](dispatch2.c)描述 `0x14230` 與 `0x1425E` 入口的局部分支、佇列狀態請求、排程請求及離開位址。`0x14230` 將 command 低 byte 與 `170／171` 對應；`0x1425E` 使用完整 unsigned 32-bit 比較。當佇列返回 0 且該路徑要求排程，模型記錄 callback `0x13F88` 與 delay 300；不宣稱排程成功或 callback 被執行。

模型假設原 dispatcher stack／暫存器有效，佇列與排程呼叫正常返回；它不重現其他暫存器、外部副作用、真正裝置、時間或實機功能，沒有用來取代候選 BIN 的機器碼。原指令連結與逐 byte 檢查見[續段來源](../tsl9-ota-dispatch2-source/README.md)。

Windows MSVC 實測 C11 與 C++17 各 1,034 案例，包含全部 256 byte command、兩種合成佇列回覆及數個較大值；另用 `python experiments/tsl9-dispatch2-model/verify_instructions.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 核對 27 條原指令。可在安裝 C 編譯器的環境使用 `cc -std=c11 -Iexperiments/tsl9-dispatch2-model experiments/tsl9-dispatch2-model/dispatch2.c experiments/tsl9-dispatch2-model/test_dispatch2.c -o test-dispatch2` 編譯並執行測試；此 POSIX 指令尚未實測。
