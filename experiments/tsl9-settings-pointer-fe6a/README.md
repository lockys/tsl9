# `0xFE6A` 設定指標位址用途

原始函式 `[0xFE6A,0xFF44)` 共 72 條線性指令。`0xFE6A` 取得 `GP+84` 的儲存位址並讀取指標；若 `0xFE76` 分支不成立，`0xFE82` 將該儲存位址複製到 `s0`，之後 `0xFEB4` 透過 `s0` 再次讀取指標。整個窗口內 `s0` 的其他兩處用途是 stack 保存與恢復。

窗口內九條明確 store 中，三條寫 stack、六條直接寫 `GP+288／291／292／296`，沒有直接寫 `GP+[84,88)`。因此在 GP 穩定、stack 三個寫入區不與指標重疊、儲存暫存器與記憶體符合約定的條件下，這些**函式內明確 store**不改寫指標。函式有多次外部呼叫，callee、副作用、其他入口、例外、實機 RAM 與中斷均未封閉，不能推論全域指標不變。

`python experiments/tsl9-settings-pointer-fe6a/verify.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 固定候選雜湊，核對完整線性窗口的 `s0` 用途、所有明確 store、關鍵分支與合成負例；不執行韌體。

## 呼叫目標

`0x828C`、`0x81EE` 與 `0xA9DE` 的完整短函式分別只讀取固定 byte 並返回，不執行 store。`0x81B0` 除 stack 保存外，會間接呼叫 `0x4007C`；`0x90B0` 的明確 store 包含三次 stack 保存與兩次清除工作表欄位。該表從 `0x2000BE08` 起，依正常流程以 12-byte stride 掃描最多 15 項；在 index／保存暫存器保持及有效記憶體的條件下，兩個欄位寫入均不與 `GP+[84,88)` 重疊。`0x90B0` 仍可能呼叫 `0x40068` 並尾跳 `0x4005C`，故其完整副作用未閉合。

使用同樣參數執行 `python experiments/tsl9-settings-pointer-fe6a/verify-callees.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 可核對這些函式與位置；stack 別名、resident 槽、例外及硬體仍未驗證。
