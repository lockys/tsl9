# `0xFE6A` 設定指標位址用途

原始函式 `[0xFE6A,0xFF44)` 共 72 條線性指令。`0xFE6A` 取得 `GP+84` 的儲存位址並讀取指標；若 `0xFE76` 分支不成立，`0xFE82` 將該儲存位址複製到 `s0`，之後 `0xFEB4` 透過 `s0` 再次讀取指標。整個窗口內 `s0` 的其他兩處用途是 stack 保存與恢復。

窗口內九條明確 store 中，三條寫 stack、六條直接寫 `GP+288／291／292／296`，沒有直接寫 `GP+[84,88)`。因此在 GP 穩定、stack 三個寫入區不與指標重疊、儲存暫存器與記憶體符合約定的條件下，這些**函式內明確 store**不改寫指標。函式有多次外部呼叫，callee、副作用、其他入口、例外、實機 RAM 與中斷均未封閉，不能推論全域指標不變。

`python experiments/tsl9-settings-pointer-fe6a/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 固定候選雜湊，核對完整線性窗口的 `s0` 用途、所有明確 store、關鍵分支與合成負例；不執行韌體。
