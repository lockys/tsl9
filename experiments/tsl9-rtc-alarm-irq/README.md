# RTC alarm IRQ 原機重建

[English](readme.en.md) · [來源](src/rtc_alarm.v1.c) · [規格](spec-v1.json) · [整合結果](../../analysis/rtc-alarm-irq-2026-10-24/README.md)

原 BIN 的五段 78B／23 指令已分別編譯為 C11、C++17。62 個非控制轉移 bytes 相同；四個具型別直接轉移依原位址編碼後，全部 78 bytes 相同。保留 GP+392、原始半字輪詢、遮罩清除、尾跳與 MRET。未執行目標、模擬 ISA、連硬體或網路；未產生韌體 BIN。

原生物件仍有四筆 relocation；這不代表已產生可執行的原位址映像。物理晶片、ROM、frame／IRQ 契約、輪詢終止與 OTA 尚未證明。以既有 LLVM 工具路徑變數執行：

```sh
python3 experiments/tsl9-rtc-alarm-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rtc-alarm-irq/build/trial-v1
python3 experiments/tsl9-rtc-alarm-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rtc-alarm-irq/build/component-v1
python3 scripts/check-rtc-alarm-irq-publication.py
```

驗證工具為 Windows Android NDK 27.1.12297006／LLVM18，依賴固定雜湊與 `.exe`；未驗證其他系統。收據保留本機，缺少封存產物時重播不會下載或重建它們。
