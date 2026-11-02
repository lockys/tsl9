# 0x14056 命令分派的局部重建

[English](readme.en.md)

原始候選程式在 `0x14062..0x140B6` 比較 byte 命令；`0x45`、`0x52`、`0x53`、`0x55`、`0x57` 走到 `0x1408E`，再由 `0x14094` 呼叫 `0x9C4A`。呼叫者 `0x8A48` 指向 `0x14056`。這是局部分派證據，不能單憑命令值認定完整 OTA 語意。

[`src` 中的 C/C++ 模型](../../src/native/receive/ota_dispatch_14056.inc)只辨識此五種轉交情況，沒有實作其他分支或呼叫硬體。驗證器核對實際反組譯的關鍵指令，再將模型編譯為 WebAssembly，以合成輸入涵蓋全部 256 種 byte；這是模型測試，沒有執行韌體。

`python scripts/verify-ota-dispatch-14056.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`

此模型尚未連入候選映像，也沒有取代原始資料載體。完整 ABI、其他命令、非正常入口、硬體與 OTA 相容性仍未驗證。避免在輸出中披露可能的驗證資料。
