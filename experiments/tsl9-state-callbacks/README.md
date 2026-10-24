# 狀態讀取與輔助函式

[English](readme.en.md)

由原廠 ID2966 V4.1.60 BIN 的 27 個狀態事件讀取入口與 2 個實際呼叫的輔助函式重建。共 472 bytes、153 條指令、45 個架構基本區塊。C11／C++17 的原生物件一致；438 bytes 非控制指令直接相符，10 個分支／呼叫經靜態原位址編碼後，全部 472 bytes 與原始 BIN 相符。

[主要來源](../../src/native/receive/state_leaf_reads.c) · [原始指令證據](../../analysis/state-callbacks-2026-10-24/leaf-evidence.json) · [原生編譯收據](build/native-v1/measurement.json)

保留 AUIPC／GP 讀取、讀取寬度、條件位元組合、兩個真實輔助呼叫，以及 B082 的 16-byte 堆疊與 RA 保存／還原。這些函式是原始架構區塊，包含刻意相鄰的 fall-through，不能當成獨立的一般 C API 執行。

以本機 LLVM bin 路徑取代變數後，可用 `python build-v1.py --tool-dir "$LLVM_BIN" --replay build/native-v1` 重查既有編譯證據。新編譯使用 `--trial <新的目錄名稱>`。

尚未證明：狀態欄位的實際用途、RAM 擁有權與映射、私有 ABI、原址配置、MCU／ROM／中斷與 OTA 相容性。未執行目標、模型或 ISA 模擬，未接觸硬體，未產生可燒錄 BIN。

## 目前整合

[整合證據](../../analysis/state-callback-integration-2026-10-24/README.md)：12224B code＋516B data／807RELA／79UND。可用 integrate-v1.py --tool-dir "$LLVM_BIN" --replay build/component-v1 重查。仍是 VMA=0 的不可執行部分連結物件，未證明原機相容性。
