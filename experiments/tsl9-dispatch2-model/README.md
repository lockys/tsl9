# 命令分流續段的 C 行為模型

[模型](dispatch2.c)描述 `0x14230` 與 `0x1425E` 入口的局部分支、狀態 byte 讀取、排程請求及離開位址。`0x14230` 將 command 低 byte 與 `170／171` 對應；`0x1425E` 使用完整 unsigned 32-bit 比較。當狀態 byte 為 0 且該路徑要求排程，模型記錄 callback `0x13F88` 與 delay 300；不宣稱排程成功或 callback 被執行。

模型假設原 dispatcher stack／暫存器有效，狀態讀取與排程呼叫正常返回；它不重現其他暫存器、外部副作用、真正裝置、時間或實機功能，沒有用來取代候選 BIN 的機器碼。原指令連結與逐 byte 檢查見[續段來源](../tsl9-ota-dispatch2-source/README.md)。

Windows MSVC 實測 C11 與 C++17 各 131,082 案例，包含全部 256 byte command、全部 256 個合成狀態 byte及數個較大值；另用 `python experiments/tsl9-dispatch2-model/verify_instructions.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 核對 36 條原指令。可在安裝 C 編譯器的環境使用 `cc -std=c11 -Iexperiments/tsl9-dispatch2-model experiments/tsl9-dispatch2-model/dispatch2.c experiments/tsl9-dispatch2-model/test_dispatch2.c -o test-dispatch2` 編譯並執行測試；此 POSIX 指令尚未實測。

`0x81AA` 只讀取 `GP+167` 的 unsigned byte；目前無足夠證據稱它為佇列狀態。若 reset 清零完成、GP 為 `0x20004000` 且此 byte 在讀取前未被改寫，該次讀取為 0；這不證明讀取當時的實機狀態或排程成功。

[後續直接寫入掃描](../tsl9-state167-writers/README.md)找到 `0x93A2` 將 `seqz` 的 0／1 結果寫入此 byte；全域值域仍受其他寫入與非同步條件限制。
