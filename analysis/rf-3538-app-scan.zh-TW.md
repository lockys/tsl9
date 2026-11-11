# APP 對候選 0x20003538 的有界初始化追查

**結論：未在此掃描模式找到 APP explicit target-overlapping store；不是無 writer 證明。** 候選 resident startup 有條件 zero writer，非零 pointer 的來源、當時值及容量仍未知。即使假設該 RAM 為 resident 私有，也只能在此假設與候選 image 條件內解讀，不能用所有權假設排除 APP、其他 agent 或 alias 寫入。

## Caller-supplied record 的生存見證

原始 APP `0x175E8..0x17666` 在 stack 準備 32-byte record，`0x17644/17648` 的 AUIPC/ADDI 得 `0x174EE`，`0x1764C` 寫 `SP+16`，`0x17658` 設 `a0=sp`，`0x1765A` 經 slot `0x401C4` 間接呼叫。實際固定 bytes `0x17644..0x1765C` 為 `970700009387a7ea3ec89147a30cf1008327441c0a858297`。見 [APP bridge](../experiments/tsl9-original-RF-bridge/README.md)；此見證是 caller record／callback，不是 target writer。

若 slot 確實接候選 RF_Config，且 guard、callee、有效不重疊記憶體及 copy 契約均成立，32 bytes 被複製到 `[0x20003540,0x20003560)`；callback 到 `0x20003550`。target `[0x20003538,0x2000353C)` 在目的地之前 8 bytes，故這次已識別 copy 不寫 target。這不排除其他 caller、間接副作用、動態 alias 或不同 resident。startup zero 的先決條件及來源缺口見 [初始化覆蓋](rf-3538-init-coverage.zh-TW.md)。

## 固定 APP 全檔語法掃描

`scripts/scan-app-rf-3538.py` 對 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 驗證 76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，offset 0 對應 `0x8000`，掃 `[0x8000,0x1AC00)` 全部 halfword 起點；包含資料與指令中間，並非已辨識 code 或 reachability。

沿用 `scan-rf-pointer-forward.py`：每個起點獨立、最多 32 條；傳播 LUI/AUIPC、ADDI/ADD、部分 compressed move/immediate，辨識一般 byte/half/word store 與 C.SW，檢查任一 store byte 與 target 重疊；load 目的變 unknown，不支援指令或控制流立即終止且清除所有 facts。這不是完整 ISA、CFG、指標分析或執行。結果 38400 起點、71453 次指令檢查、38400 路徑 unknown/control stop、22914 個不同 stop PC、0 budget/range-end stop，target store 命中 0。stop 次數是候選路徑次數，不表示真實執行次數。合成 LUI→ADDI→SW 可生存並命中；插入 unknown 即終止，故 unknown 不被當作無寫入。

尤其未涵蓋跨分支/呼叫常數、GP/SP 或載入的 pointer、bulk copy/zero、未支援壓縮指令與其他 ISA、DMA/interrupt、其他 firmware 或執行時改寫。APP 資料中的假解碼也不證明 code。APP witness 與候選 resident 的聯結仍為條件性，不是設備觀測。

## 測試

`python scripts/scan-app-rf-3538.py`；`python -m unittest discover -s tests -p test_app_rf_3538_scan.py -v`。測試固定影像／caller bytes、長度與 hash mutation、合成傳播 store 和 unknown 阻斷；合成 store 不是實際 writer。純 host 靜態分析，沒有硬體操作或修改輸入。
