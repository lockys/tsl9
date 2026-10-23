# 周邊寫入與接收分派部分連結

[English](readme.en.md)

把既有 950B 分派組件與 212B 周邊寫入原生物件實際部分連結：1162B、402 條指令、49 個真實 FUNC。保留冷路徑、所有輸入函式本體及 57 個 pending RELA，剩餘 5 個真實 UND。新增提供者位於組件偏移 950，既有呼叫位於偏移 888；兩者由實際輸入物件核對。

此為診斷 VMA0 的 `ld.lld -r --no-relax` 組件。符號配對不等於機器控制位移已解決，也未證明普通 C ABI、原始擺放、ROM、矽晶或 OTA 相容性。沒有產生或執行 BIN，不能作為可燒錄韌體。

`build.py` 只讀取兩組既有正式物件，重新完整檢查上游收據，並各執行一次 linker 與 LLVM readback；不重新編譯。每個語言的輸出使用全新目錄，保存實際命令、日誌、物件及收據。檢查涵蓋完整來源與工具閉包、所有本體、符號、重定位、原韌體固定位元、控制型別及 402 條 readback。負向回歸直接修改記憶體內 ELF 或型別輸入，不依賴整檔雜湊。原韌體與原物件均不更動。

```sh
python3 experiments/tsl9-peripheral-dispatch-component/build.py \
  --project-root "$TSL9_ROOT" --llvm-bin "$LLVM_BIN" \
  --dispatch-root "$TSL9_ROOT/experiments/tsl9-record-dispatch-component/build/component-v1" \
  --peripheral-root "$TSL9_ROOT/experiments/tsl9-peripheral-write/build/verified-v2" \
  --build-root "$TSL9_ROOT/experiments/tsl9-peripheral-dispatch-component/build/component-v1"
python3 experiments/tsl9-peripheral-dispatch-component/check.py \
  --project-root "$TSL9_ROOT" --llvm-bin "$LLVM_BIN" \
  --replay "$TSL9_ROOT/experiments/tsl9-peripheral-dispatch-component/build/component-v1/c/verification.json"
```

C++ 使用同一命令，收據路徑中的 `c` 改為 `cpp`。`--require-firmware-ready` 在完整靜態檢查後仍應拒絕。預設檢查僅驗證來源封存，不代表曾執行 linker。失敗的輸出會保留，不覆寫或無限重試。公開衍生收據由專案發布流程處理，原始本機收據不可偽稱為公開匿名原件。
