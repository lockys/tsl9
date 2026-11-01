# 已選來源區段的指令解碼

[English](readme.en.md)

`python scripts/verify-selected-instruction-decode.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 從來源重建不可燒錄診斷 ELF，再以明示 `+m,+a,+c,+zicsr,+zifencei` 的 LLVM 解碼其已選可執行區段。C／C++ 各解碼 23,602 條、未知指令為零，沒有觀察到 `fence.i`；合成無效指令的負向測試會被辨識為未知。檢查不讀候選檔或排除區，不執行目標。

診斷 ELF 不保留 RISC-V 架構屬性；未指定指令集時，部分乘法等指令可能顯示為未知，不能直接推論映像損壞。WCH 的 [QingKe V4 手冊頁](https://www.wch-ic.com/downloads/QingKeV4_Processor_Manual_PDF.html)說明 V4 系列支援 RV32IMAC，並列 CH32V208 使用 V4C。這支持選擇基本解碼方向；`zicsr`／`zifencei` 是本次明示的解碼假設，不能單憑工具輸出證明目標晶片支援每個 CSR 或副作用。

線性解碼不是控制流程、原始 ABI、執行結果或實機相容性驗證；未選／排除區不在檢查範圍。完整 BIN 與七項嚴格連結依賴仍未完成，輸出不可燒錄。
