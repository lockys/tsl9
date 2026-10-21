# 最終原生收據與獨立 ABI 證據綁定

本綁定重新檢查最終 `native-sealed-inputs/{c,cpp}` 的六個實際物件、IR與元件ELF，結果與不可變的上一層 ABI 審查完全一致，只在記憶體內正規化兩個位置標籤。沒有改寫上一層封存證據。正式收據為 `350c0025…f4fa19`／`a66ba2e7…ed848`，元件ELF為 `aeccc19d…0339d`。[English](readme.en.md)

程式化函式為100 B／38條靜態指令，正常返回契約、讀取後且寫入前的A0對齊、五個已知內部迴圈位置通過；每種語言仍有12個機器碼及3個IR反例拒絕。完整因果分析、94／102 B診斷結果與原始metadata見上一層文件。相同尺寸沒有保留原始 `+8` 指令邊界，scratch暫存器、完整失敗／不返回前綴、中斷與完整映像仍未證明等價。

執行 `python replay.py --check`。可另以 `--context-json` 指定 `project_root`、`prior_build`、`firmware`、`source_dir`、`parser`與依語言指定的 `build_roots`；此審查確實將韌體路徑傳至原始SHA檢查，不呼叫產製器的重播路由。產製器目前封存版本的 `--replay` 只保證其預設參考韌體路徑；非預設 `--firmware` 轉送限制仍有記錄，沒有藉此放寬本審查。

這是離線靜態元件證據，不是完整可燒錄韌體。沒有執行RV32、模擬、連網、操作硬體或產生BIN。
