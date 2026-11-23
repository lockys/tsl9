# v4.1.60：第 13 列重播的上游記錄 ID

根據原 decoded BIN（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`），APP 映射基底 `0x8000`：

| 記錄首 halfword | 分派轉移 | 送入 0xd578 的 a0 | 送入 0xd578 的 a1 |
|---|---|---|---|
| 325 / 0x145 | 0x150ae → 0xd632 | (halfword[record+6] >> 6) & 1 | byte[record+8] >= 38 |
| 925 / 0x39d | 0x14f72 → 0xd64a | (halfword[record+4] >> 9) & 1 | byte[record+6] >= 81 |

`0x14d5e` 從 s0 指向的記錄讀首 halfword；325 的比較在 `0x14d7a–0x14d7e`，925 的比較在 `0x14f62–0x14f66`。兩處分派先以 s0 設 a0，再恢復堆疊及 ra，以 `jal x0` 尾跳，非普通 call。兩入口抽取欄位後各自尾跳 `0xd578`。全檔每半字位置對 JAL、C.JAL、C.J 編碼掃描，目標為兩入口的直接命中只有列出的兩處；掃描可能包含資料或指令後半部，不排除間接跳轉與外部映像。

一條可靜態追溯的上游路徑從 `0x12c58` 起檢查 32 個 12-byte 槽，對非空記錄請求複製到堆疊並清除原槽首 halfword；在 `0x82d2` 返回零、記錄首 halfword 非 1、相關設定 bit 3 為零及 `0x81aa` 返回非零等條件下，`0x12d8c` 呼叫 `0x14d2e`。該分派器取得模式 byte 為 1 時經地址表和間接跳轉進入上述比較樹。複製/provider 正常返回、記憶體不受干擾及所有分支條件均為限制，不是設備實際執行的證據，亦不能將未知外部輸入稱為已觀察事件。

本機 `analysis/check_v4160_row13_upstream_ids.py` 核對 BIN 雜湊、兩個選定 ID 指令窗、325 的 branch 及兩個 tail-jump 目標；一般及 Python `-O` 均通過。它不是完整控制流或獨立 CPU 驗證。未修改原 BIN、正式來源及既有 staged 工作，未連接設備。
