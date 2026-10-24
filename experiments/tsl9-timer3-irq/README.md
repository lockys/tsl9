# TIM3 IRQ 原機區域重建

[English](readme.en.md) · [來源](src/timer3_irq.v1.c) · [規格](spec-v1.json) · [整合結果](../../analysis/timer3-irq-2026-10-24/README.md)

原 979E–9958 的 442B／138 指令，分成 32 個具明確 fallthrough 順序的架構區域。C11／C++17 實際產物的 376 個非控制 bytes 相同；24 個具型別直接轉移依原位址靜態編碼後，全部 442 bytes 相同。

這些區域不是可獨立呼叫的一般 C 函式。C unsigned 運算與 volatile 讀寫搭配明確 SP／S-register／AUIPC／DIV／呼叫埠；保留 16B frame、S0／S1／S2、signed DIV 與 MRET。兩個間接來源是固定 word40068 與當下 S2+12，函式身分仍未知。

使用已安裝且雜湊符合規格的 Windows LLVM 工具目錄變數：

```sh
python3 experiments/tsl9-timer3-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/trial-v1
python3 experiments/tsl9-timer3-irq/select-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/providers-v1
python3 experiments/tsl9-timer3-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-timer3-irq/build/component-v1
python3 scripts/check-timer3-irq-publication.py
```

驗證工具為 Android NDK 27.1.12297006／LLVM18，依賴固定雜湊與 `.exe`，未驗證其他系統。缺少本機產物時，重播不會下載或重建它們。helper 選取保留四個真實完整函式共 60B，沒有產生假 provider。

未執行目標、HOST 或 ISA 模擬，未連硬體或網路。實體晶片、resident、IRQ ABI、原位址與 RAM 配置、完整啟動／OTA 未證；不產生可刷 BIN。
