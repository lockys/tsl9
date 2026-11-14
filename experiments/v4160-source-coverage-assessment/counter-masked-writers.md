# Counter 的兩個局部 masked 寫入

`counter-masked-writers.py` 固定原 BIN SHA-256，取得 `0xa0f2–0xa0fe` 與 `0xa33a–0xa348` 的原始 bytes。受限指令投影逐步處理 byte 載入、加一、AND 3 和 byte 寫入；第二個片段還在寫入前讀一次 `sp+8` word。兩片段各測全部 256 個輸入、四種合成 GP（含 32-bit 環繞）與兩種堆疊值，共 4,096 條事件軌跡，寫入結果均為 `(原 byte+1)&3`。

結果僅涵蓋從各片段開頭正常順序執行、讀寫成功且沒有干擾的情形；合成堆疊與 counter 位址不重疊。這不證明只能從這些入口進入、其他路徑／resident／中斷不會寫入，也不證明讀取前的值恆為 0–3。未新增覆蓋、provider alias 或實機結論。
