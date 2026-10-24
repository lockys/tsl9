# main／application／初始化原機重建

[English](readme.en.md) · [來源](src/main_family.v1.c) · [規格](spec-v1.json) · [整合結果](../../analysis/main-family-2026-10-24/README.md)

三段原始範圍：8180–81AA 應用迴圈 42B／15i、9008–901A main 18B／8i、9250–9290 初始化 64B／19i。共 124B／42 指令、23 個具明確相鄰順序的架構區域。C11／C++17 的 52 個非控制 bytes 相同，20 個具型別轉移依原位址靜態編碼後全部相同。

保留三個原 16B frame、RA 與 S-register 埠、應用迴圈中的當下 S2+0 回呼、看門狗寫入，以及初始化末端到 17BF6 的無 link 尾跳。這些不是可獨立呼叫的一般 C 函式，未證明 entry／provider ABI 或實際 callback 身分。

使用已安裝且雜湊符合規格的 Windows LLVM 目錄變數：

```sh
python3 experiments/tsl9-main-family/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/trial-v2
python3 experiments/tsl9-main-family/select-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/providers-v1
python3 experiments/tsl9-main-family/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-family/build/component-v1
python3 scripts/check-main-family-publication.py
```

已驗證 Android NDK 27.1.12297006／LLVM18 的固定工具；原生流程目前依賴 `.exe`，未驗證跨系統重播。正式單體收據為 trial-v2；trial-v1 是多段範圍驗證器修正前的不完整試編譯，未作為通過證據。來源本身未因此變更。缺少本機收據／產物時，重播不會下載或重建。

未執行目標、HOST 或 ISA 模擬，未連硬體或網路。實體晶片／ROM、原位址與 RAM、完整啟動及 BLE OTA 未證明，不產生可刷 BIN。
