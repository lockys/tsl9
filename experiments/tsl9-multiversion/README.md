# 22 份 BIN 的跨版本 C/C++ 重建：第一輪

已從實際解碼 BIN 辨識出一個完整的 42B／15 條 RISC-V 指令函式，並將其值層邏輯整理成可讀 C11／C++17。15 份 Runtime 的此函式逐 byte 相同且在各自映像唯一出現；並未宣稱 15 份整體韌體等價。原 R81 程式及連結限制保持。

`src/observed_predicate.c` 的輸入是呼叫者提供的設定位元組、32 位無號索引與三個狀態位元組。邏輯是：設定 byte4 的 bit3 為 1 → 0；索引大於 2 → 0；否則狀態值為 0、1、2 → 1，其餘 → 0。原函式的 GP 相對讀取見 `evidence/predicate.json` 的完整指令及各映像位置；此可攜實作不解參考實體記憶體。它位於既有免打擾模型的呼叫鏈，但這不足以證明完整免打擾行為或原機功能。

`src/observed_profiles.c` 僅記錄 15 份精確匹配來源的 FirmwareID、檔案 offset、大小與 SHA256。查詢未知或未匹配 ID 回傳空指標；此表不是硬體選型、相容判斷或燒錄工具。FirmwareID 2601、2603、2613 未找到完全相同的函式，不能據此宣稱功能被移除或已找到等價替代。四份 12KB 映像亦不套用此函式。

## 本機驗證

在此資料夾執行 `python verify.py`，或以 `--firmware-root <BINs絕對路徑>` 指定已封存的 22 份解碼 BIN。預設資料來自 `../../firmware-downloads/legacy-options-2026-10-20/BINs`。需既有 Windows x64 Python、ctypes 及 Android NDK 27.1.12297006 的 clang／lld；腳本不下載工具、不連網。

驗證先逐份核對來源 SHA256、42B 完整匹配與位置，再把新增純函式編譯成 Windows x64 主機 DLL，遍歷全部 256 設定值 × 3 索引 × 256 狀態值，另查無號索引界限、短路讀取及來源表。C11、C++17 各執行；RV32IMAC 僅編譯成 relocatable object，不執行。輸出在唯一 `build/<run>/verification.json`。

這些是新增純函式的主機測試與原始 bytes 靜態核對，沒有執行／模擬原 BIN，也沒有證實記憶體有效性、完整 caller 行為、MCU、ROM、IRQ、BLE 或 OTA。此輪不產生可燒錄 BIN。跨版本資料不能直接補入 V4.1.00 缺失的 lookup 尾端，也不能替代未知 ROM。
