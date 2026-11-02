# 狀態 byte 寫入的比較模型

`0x937E` 呼叫 `0x9E84`，將其回傳的第一個 32-bit word 存入 stack，並以 little-endian halfword 讀取其高 16 bits；再呼叫 `0x9334`，將得到的完整 32-bit 返回值與前述 16-bit 值相減，`seqz` 的 0／1 結果寫入 `GP+167`。此解讀依 stack 有效、little-endian、正常呼叫及暫存器未被干擾成立。`0x9E84` 本身透過 `0x4004C` 間接槽請求讀取資料；兩個已辨識的直接呼叫點是 `0x9F06` 與 `0x9F42`。

[便攜 C 模型](state167.c)只描述兩個輸入的比較，並不取得或推斷實體資料、實作 resident 或重現其他副作用。Windows MSVC 的 C11／C++17 各執行 196,610 個合成案例，涵蓋所有高 16-bit 值及超出 16-bit 的比較值。`python experiments/tsl9-state167-compare/verify_instructions.py --firmware <CANDIDATE_BIN> --r2 <R2_EXECUTABLE>` 核對 21 條指令，包含合成負例；未執行 firmware 或讀取裝置資料。

實際來源資料、間接槽、其他寫入與此狀態的產品語義仍未確認；此模型未整合至候選 BIN。
