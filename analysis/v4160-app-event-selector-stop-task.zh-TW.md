# v4.1.60：清理路徑的 `[0x4005c]` 在 V1.31 候選中不派發

接續[寫零前的 APP 回呼表清理](v4160-app-event-selector-prezero-callback.zh-TW.md)。APP `0x9106` 載入 `[0x4005c]`，`0x910e` 尾跳。WCH V1.31 候選該 word 為 `0x439a8`，對應既有[停止事件模型](../experiments/tsl9-resident-message-queue/README.md)。本輪從原始候選 bytes 核對呼叫閉包，而不是僅採用函式名稱。

- `0x439cc` 以 AUIPC/JALR 固定轉到 `0x20000314`（flash 來源 `0x40584`）。在候選程式碼已複製及 Xwchc 解碼成立時，該 helper 查找對應 task/event 的節點，不呼叫 handler。找到節點時，`0x439d4` 清零其 `+2` 的 event halfword。
- `0x439dc` 無論有無找到節點都呼叫 `0x4358a`。有效 task 下，它依 `pending &= ~mask` 更新 pending 事件；無效 task 返回 `3`，不更新 pending。這依賴候選 Xwchc 資料指令解釋與正常存取。
- 若 task 等於當前 task index，外層另外把 mask OR 入當前 clear-mask。外層返回 `0` 或 `6`，以 lookup 是否找到節點決定，不是內層 clear-event 的回傳碼。這三段的呼叫邊僅為上述兩個固定目標，沒有從 handler table 載入再呼叫的路徑。

結論：若 APP 執行時的 slot 和 RAM helper 符合這份候選，這一步會嘗試停止／清除事件，不會由這條呼叫鏈同步派發 `0x176f8`。硬體時序、其他上下文與剩餘的 `[0x40068]` 分支不在此結論內。下一步核對 V1.31 候選 `[0x40068]` 的下游控制流，補齊同一個 `0x90b0` 命中分支。

Python `-O` 通過原 APP 與 V1.31 候選的 SHA-256、APP 尾跳、候選 slot word、三段共 206 bytes 及兩個 helper 目標。候選 SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`；未連設備或修改 BIN／正式來源。
