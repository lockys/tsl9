# 控制門控、模式與回呼

[English](readme.en.md)

本輪重建十二個完整函式，892B／308 指令；C11、C++17 物件相同。主元件接上五個舊入口，沒有新增依賴，剩餘提供者由 173 降至 168。原生配置後，35,440B code／data 逐 byte 與官方 BIN 相同。**產物仍是 entry=0、PT_LOAD=0 的診斷 ELF，不是可刷韌體。**

| 原始入口 | 已確認的靜態行為 |
| --- | --- |
| `81EE`、`A658`、`A9DE` | 條件 byte 讀取與 pending byte 設定 |
| `CD6A` | 位元圖 `0x65E` 分派、完整參數比較與後續呼叫 |
| `D07C`、`D0EE` | 條件門控、三個 word 常數與 ROM 槽位參數 |
| `FD6A`、`FDF6`、`10022` | 模式切換、完整零值判斷與有序 byte 寫入 |
| `FB1E`、`FB5E`、`FE6A` | 自排程／交叉取消回呼、模式與計數差值判斷 |

保留的關鍵細節：`FD6A` 只對完整參數值 3 執行切換；`D07C` 不把完整參數提前縮成 byte。`FE6A` 在呼叫後重新讀取設定與儲存的計數值，使用 `uint32(fresh-stored)>1499`；排程數值 1500 的單位仍未知。兩個回呼及取消順序均保留，沒有用猜測的產品功能名稱取代數值狀態。

[原始指令](evidence.json)、[135 個語意核對點](provider-contracts.json)、[結果與收據雜湊](summary.json)、[剩餘依賴](next-providers.json)、[唯讀診斷候選](feature-candidates.json)。候選功能包括顯示分派／略過原因、模式與計數狀態、回呼關係；目前只有靜態報告，尚未接入硬體。

125 個 C/H 檔通過 198 組比較／396 個物件；舊 124 檔不變。流程核對 11,786 指令、2,021 直接轉移，沒有一般續行缺口；1,824 個目標已有重建實作，197 個仍只引用原位址。間接執行目標、IRQ 返回、EBREAK／向量邊界及實際可達性仍未證明。

從 repository 根目錄執行唯讀檢查：

```sh
python scripts/verify-curated-source.py
python experiments/tsl9-control-gates/derive-v1.py --counts
```

工具與標頭雜湊固定於 `spec-v1.json`。指定符合配方的既有 `LLVM_BIN`，可用 `build-v1.py --tool-dir "$LLVM_BIN" --trial <new-name>` 建立新試驗；完整整合重播另需本機歷次收據。本輪沒有執行目標、HOST 模型、ISA 模擬或硬體操作，沒有新增 BIN。實體晶片、啟動／ROM／RAM／IRQ 與原 OTA 相容性仍未通過。
