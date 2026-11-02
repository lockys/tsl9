# 分流分支的條件式 C 模型

此[模型](dispatch3.c)描述 `0x14288..0x142C0` 的局部分支：command 為 162 時轉至 `0x149FC`；不是 163 時轉至 `0x14098`；163 且 length 為 76 時請求配置 76 bytes，非零結果才請求將 76 bytes 從原 `s0` 指標複製至配置結果。模型只記錄合成位址與請求，不讀寫這些位址，也不處理後續執行或副作用。

固定版本 WCH 標頭把 `0x40070` 對應的 slot 15 宣告為 `tmos_msg_allocate(uint16_t len)`，把 `0x4004C` 的 slot 6 宣告為 `tmos_memcpy`。固定 V1.31 參考的槽數值分別為 `0x20000236` 與 `0x20000332`。這是候選接口對照；不證明實機 ROM、配置結果、記憶體有效性或複製成功。模型假設呼叫正常返回、原 stack／暫存器有效且未受干擾。

Windows MSVC C11／C++17 各測試 1,538 個合成案例。`python experiments/tsl9-dispatch3-model/verify_instructions.py --firmware <CANDIDATE_BIN> --resident <REFERENCE_BIN> --header <WCH_HEADER> --r2 <R2_EXECUTABLE>` 核對 17 條指令、兩個參考槽及固定標頭。此模型未整合進候選 BIN，沒有執行韌體或操作硬體。
