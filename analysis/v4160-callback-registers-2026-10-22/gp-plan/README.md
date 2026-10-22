# 為何改成讀取 live GP

[English](readme.en.md)

固定 S10／S11、仍使用舊 GP 快照橋接的 656-byte 實際元件，有十六個 `C.MV rd,GP`：入口一次，以及十五個不透明呼叫後各一次，共 32 bytes。`first-fixed-GP-copies.json` 由實際 ELF 的 halfword 欄位讀出這些來源暫存器，不是以文字搜尋宣稱指令存在。

這項觀察本身不證明可直接刪除指令。舊橋接把 GP 快照存進 C 欄位；新來源必須將六個真正使用 GP 的位置改為讀取當下的實體 GP，並移除不再使用的 native 快照。不能假設 callee 保存 GP，也不能讓編譯器沿用呼叫前的 GP scalar。HOST 的六個 accessor 仍必須對應原本同一個 mutable 欄位；既有 HOST 成績與新原生驗證分開報告。

新變體的六個用途為兩個 context byte read、計算 lane 後的 connection halfword read、兩次 GP+128 引數，以及 GP+42 的 halfword read 後存進描述欄位。來源／獨立 ABI 審查另驗 IR 的 volatile register read、真實指令寬度、沒有 GP 寫入，以及每次不透明呼叫前後的使用位置。Clang 將最後一個 LHU 降成 LH，隨後的 low16 store 可對應，但不能宣稱中間實體 GPR 的 sign-prefix 完全相同。

這是一般 C/C++ 邏輯與窄實體暫存器橋接的改進，沒有執行原始韌體、模擬 CPU、連接硬體或讀取裝置身分。未證明原機 ROM／BOOT、完整 ABI 或 BLE OTA。
