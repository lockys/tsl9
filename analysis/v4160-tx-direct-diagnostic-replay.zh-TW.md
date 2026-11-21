# v4.1.60：將 TX 直接綁定納入診斷重跑

延續 [整圖連結對照](v4160-tx-direct-graph.zh-TW.md)。本機 `experiments/v4160-tx-direct-binding-next/graph_probe.py` 現使用診斷建置選用的觀察介面，不再依賴 Python 行號或 frame tracing。只有四個正向 stock-lane 輸出完成原有驗證後才觀察；重連結用暫存複本，原有測試照常執行。此提交只發布報告，重跑程式仍在本機。

新增檢查：直接讀取 dispatcher 輸入物件在區段偏移 `0x1e` 的 relocation，確認改名前後都是唯一 `R_RISCV_JAL`（17）、addend=0、未定義符號；只有從 `tsl9_dispatch23_filter_8a56` 改成 `tsl9_filter_external_8a56`。連結後沿用診斷建置的區段放置檢查與 JAL 稽核，不以符號同地址推論綁定。

帶 relocation 檢查的普通模式重跑：C/C++ 基準與候選各 6,352 區段、76,800 bytes 不變、舊別名不存在；四路的符號 local 化與丟棄 TX 區段均被拒絕。啟用觀察介面後、加入 relocation 檢查前已另跑 `-O`，同樣得到四路結果。關閉觀察介面時，既有基準正向和負向控制的整合測試 `test_both_baseline_final_links_and_negative_controls` 另行通過（1 項）；整套測試未在當次時限內跑完。

主驗收仍有六項失敗，正向診斷沒有 PT_LOAD，也不是可刷映像。下一輪單獨處理符號元資料與 `.llvm_addrsig`，不把缺少符號表連結的 ordinal 當成已驗證身分。
