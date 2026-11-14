# `0xf7` 至 provider 邊界的條件性串接

`case_f7_composition.py` 串接前段閘門、分派和 `0xf7` provider 呼叫的既有投影。固定輸入 byte 為 `0xf7`，窮舉 256 個狀態 byte、256 個 `[gp+358]` 值與四個合成物件指標；在此模型中，到達 `[0x40068]` 呼叫邊界當且僅當狀態 bit 3 為零、`[gp+358]` 為零、`[0x2000becc]` 非零。以兩個不同 a1 執行這些條件，384 組在 provider 呼叫邊界仍保留差異；其他合成情況依前段退出或不呼叫該 provider。

實驗先核對各段所釘住的原 BIN 編碼與雜湊，但呼叫邊界間是重新組合的獨立投影，不是連續 CPU 執行；須假設實際讀寫成功、堆疊與狀態／表格沒有干擾性別名、狀態穩定且沒有中斷。它不證明從上游實際可達、provider 會讀 a1 或有功能差異，更不是硬體驗證。

執行 `python -I -B experiments/v4160-b0b0-pure-c-candidate/case_f7_composition.py`；`-OB` 亦通過。
