# v4.1.60 佇列 producer 的 C 候選

`producer.c` 是 `0x12bc8` 的離線語意候選，不是逐 byte 相同的建置，也未納入正式 source。它保留掃描 32 個 12-byte 槽、寫入 ID 和長度、以完整長度及 tag 呼叫 provider、正常返回後寫 tag 的順序。它不是安全佇列 API：不檢查長度，provider 可能寫到其他欄位或超出佇列。實際 provider 是否複製及其行為未知。

本機以原始 BIN（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）的受限 RV32IMC 解譯器對照 host C11/C++17：普通與 `-O` 各兩個建置、每個 4,752 筆，合計 19,008 筆比較通過。測試 provider 是可改寫合成記憶體的替身，長度 0、1、8、9、255、256 僅驗證傳參，不執行依長度複製。差分腳本與其解譯器依賴目前僅在本機，這個目錄本身不能重跑該差分。

原版 halfword 存取在候選中以兩次 byte 存取表示，不聲稱併發或原子性等價。候選為 `void`，未驗證原版返回暫存器、實際 provider、fault、interrupt、ABI 或設備行為。原始 BIN 與正式 source 均未修改。
