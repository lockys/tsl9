# 初始化尾段與共用返回區域

[English](readme.en.md) · [來源](src/init_tail.v1.c) · [規格](spec-v1.json) · [整合結果](../../analysis/init-tail-2026-10-24/README.md)

原 17B92–17BC4、17BF6–17C4E 合計 138B／47 指令，分成 10 個具明確相鄰順序的架構區域。C11／C++17 實際物件的 120 個非控制 bytes 相同，5 個具型別直接轉移依原位址靜態編碼後全部 138 bytes 相同。

保留 constructor 的 16B S0／RA frame、恢復後尾跳、GP+378 的兩條返回路徑與 fresh 讀取，以及三次 resident 間接呼叫。這些不是普通可獨立呼叫的 C 函式；未證明 entry／callee／IRQ ABI 或 resident 實作。

```sh
python3 experiments/tsl9-init-tail/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-tail/build/trial-v1
python3 experiments/tsl9-init-tail/verify-provider-v1.py --replay experiments/tsl9-init-tail/build/provider-v1
python3 experiments/tsl9-init-tail/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-tail/build/component-v1
python3 scripts/check-init-tail-publication.py
```

以已安裝且雜湊符合規格的 Windows Android NDK 27.1.12297006／LLVM18 工具核對；流程目前依賴 `.exe`，未證明跨系統重播。收據與物件留本機，重播不下載或重建缺少的產物。

未執行目標、HOST 或 ISA 模擬，未連硬體／網路，未產生可刷 BIN。原機 MCU／ROM、RAM 與原位址、完整啟動／BLE OTA 尚未證明。
