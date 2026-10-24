# 狀態事件與 callback 整合

[English](readme.en.md)

已將完整狀態事件、callback、非重複狀態存取及 27 個 getter 的實作併入保留啟動流程的離線元件。**C11／C++17 產物一致：12224B code＋516B data、4276 條原始指令、807 RELA、79 UND。**

[主要來源](../../src/native/receive/state_leaf_reads.c) · [整合檢查器](../../experiments/tsl9-state-callbacks/integrate-v1.py) · [結果與雜湊](summary.json) · [尚未解析的依賴](next-providers.json)

| 本次實際加入 | 範圍 |
| --- | --- |
| state-access | 294B／20 區塊；既有元件持有的 42B 及兩個轉移已逐 byte／參照核對，不重複加入 |
| feature-callback | 完整 314B／31 區塊，保留 checksum、計數、條件與延後回呼 |
| state-events v2 | 完整 1308B／191 區塊，保留資料組裝及立即／延後通知，包含完整 13C4E 後續流程 |
| state readers | 472B／45 區塊，27 個 getter 及兩個實際呼叫的輔助函式 |

合計新增 **2388B／815 條指令／287 區塊**。所有既有 9836B code 與 516B 資料、原本相對表及其參照均完整保留。28 個新增入口別名皆指向非零大小的真實函式；沒有用假回傳函式或 ABS 位址填補依賴。共核對 1070 個實際區塊、54 個真實入口別名與全部 807 筆轉移／資料／局部 PC-relative 參照。

接通 8 個舊依賴，新增展開 5 個真實依賴，故 82→79。下一步優先追查 D272、B0FC、12B24、13D48、10630。另有三個既有 clock／IRQ 來源名稱能對上剩餘入口，但先前原碼寬度／行為證據不足，仍未接入。

目前來源集維持 96 個 C/H、69 個 code units；連同獨立指標資料共 140 組來源比較／280 個物件。新增兩個 C/C++ 物件只用於可追溯的 state-access 選取。先前來源階段收據中的「尚未整合」欄位是該階段快照；本次元件另有獨立整合證據。

可在專案根目錄以本機 LLVM 路徑重查：

```sh
python3 experiments/tsl9-state-callbacks/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-state-callbacks/build/component-v1
```

這仍是 **ET_REL，VMA=0 的離線部分連結物件**。沒有原址配置／完整 fall-through、RAM 擁有權、私有 ABI、實體 MCU／installed ROM／中斷或 OTA 相容性證明，不能燒錄。未執行目標、模型或 ISA 模擬，未連線或接觸硬體，未產生 BIN；歷史個資問題尚存，未 commit／push。

新功能候選仍是只讀狀態診斷與韌體來源辨識；這次完成必要讀取／事件程式的整合，尚未實作診斷介面，也未確認欄位實體意義。
