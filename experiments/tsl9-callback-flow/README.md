# Callback 流程重建

[English](readme.en.md)

七個完整入口及被函式位址參照的 1061C／1333C 輔助函式，共 **1082B／368 條指令／79 區塊，另有 96B 唯讀資料**。C11／C++17 原生物件一致；60 個直接轉移、10 個 PC-relative 參照與所有選定原碼／資料均通過靜態原位址比對。

[來源](../../src/native/receive/callback_flow.c) · [指令證據](../../analysis/callback-flow-2026-10-24/evidence.json) · [規格](spec-v1.json) · [原生收據](build/native-v1/measurement.json)

完整保留 672B 的 13346 狀態組裝器及第一個 ret 後的路徑、原堆疊、fresh memory 及轉移順序。沿實際位址重用既有符號名稱；單體物件仍有 35 個外部提供者，未以假實作填補。現已接入主元件：13864B code＋674B data／930RELA／95UND。[整合證據](../../analysis/callback-flow-2026-10-24/README.md)。

```sh
python3 experiments/tsl9-callback-flow/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-flow/build/native-v1
```

這些是架構區塊，並非一般可獨立呼叫的 C ABI。欄位意義、資料界限、RAM 擁有權、installed resident／私有 ABI、原址配置、實體 MCU／ROM／中斷與 OTA 未證明。未執行目標、模型或 ISA 模擬，未連線、接觸硬體或產生 BIN。
