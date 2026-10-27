# Callback 槽的安裝、分支匯合與清除

[English](readme.en.md) · [前輪 APP task](../tsl9-original-APP-task-binding/README.md) · [既有 RF C/C++](../tsl9-original-RF-tx-path/README.md) · [既有 callback C/C++](../tsl9-resident-state8-callbacks/README.md)

本輪核對 **17 個完整 SDK 函式／5,602 bytes／1,962 指令**，串接三個額外 SDK 呼叫點。累計 **39／51 點**至少有一種具證據的條件式情境；其餘 12 點未串接。這不是所有可能 target 均已解析，也不是缺失函式數或功能完成率。[逐點清單](ledger-v1.json) · [驗證收據](verification-v1.json)

## 一個槽、七種已確認來源情境

setter `0x2000078A` 將 A0 寫入 `0x20002EF8`；非零時另將 byte `0x20002EFC` 設為 1。五個註冊點共有七種來源：

| 註冊 call pair | 最後寫入 A0 的指令 | 寫入的 target |
| --- | --- | --- |
| `0x64534` | `0x64530` | `0x645DC` |
| `0x64962` | `0x64954` | `0x65DE6` |
| `0x64E8E` | `0x64E8A` | `0x6448E` |
| `0x64E8E` | `0x64EFA` | `0x64422` |
| `0x65102` | `0x650FE` | `0x653A0` |
| `0x65102` | `0x6515E` | `0x65164` |
| `0x65508` | `0x65504` | `0x65620` |

兩個呼叫點有分支匯合，不能以單一值描述。驗證器在完整 CFG 上計算 A0 的 may-reaching-definitions；callee 保守視為可能改寫 A0，分支合併定義集合，未支援的寫入指令會停止驗證。七個最後定義都以原 LUI／ADDI encoding 獨立解碼，恰好涵蓋這五個 call pair 的全部到達定義。這是有限的靜態資料流分析，未執行 target 或模擬具體機器狀態。

每個 target 都有已重建的完整 native 本體。若其中一條註冊路徑實際到達 setter、槽值保留到 consumer load，`0x200007B4` 才可條件式對應到該 target。其他 installer、動態輸入與實際呼叫順序仍未閉合；也未證明一般 `void(void)` callback ABI。

## 返回後如何清除

consumer `0x200007A0` 先檢查指標是否為零；非零才在 `0x200007B4` 呼叫。返回後於 `0x200007BA` **重新讀取旗標**：

- 新讀值為零：在 `0x200007C4` 清除當時的 pointer 槽。
- 新讀值非零：略過清除。

setter 收到 A0=0 只清指標，**不會把旗標清零**。`0x60516` 的特定路徑在 `0x60734` 設 A0=0，釋放 32-byte frame 後以 AUIPC-T1／JALR-zero 尾跳 setter；不能改成會覆寫 RA 的普通 call，也不能把這項結論套用到該函式的所有返回路徑。

旗標還有其他寫入來源，未全部閉合。不能將這段宣稱為「一律單次呼叫」或「一定保護新 callback 不被清除」。

## 另一組 optional callback 表格

這組表格與上面的 `0x20002EF8` 槽不同：base=`0x200031C8`，五個 4-byte entries。原初始化要求將 `[0x200031C8,0x200031DC)` 清零，但實際完成與 live 零值仍未觀察。

- Slot2 `0x200031D0`：若已依原要求清零，或 RF cleanup 確實到達 `0x657C2 → 0x43B28`（A0=0、A1=2），且維持零值，guard `0x2000081C` 略過 `0x2000081E`。
- Slot0 `0x200031C8`：若初始化清零或先前正常 callback 後的 `0x2000093E` 已清零，且維持零值，guard `0x2000093A` 略過 `0x2000093C`。

Slot0 在正常 callback 返回後**直接寫零，沒有 replacement flag 檢查**。不能與前一個槽的「重新讀旗標再決定」合併。其他未保護的 array 呼叫點仍未解決。

所有結論仍要求相同 ROM／ISA／RAM profile、有效不重疊記憶體、原完整暫存器／stack／private ABI、正常返回且綁定期間無 IRQ／重入覆寫。沒有觀察 live 綁定。

本輪沿用既有 C/C++ 本體，沒有新增目標 CODE／DATA、編譯或 BIN。候選仍為 **35,324 CODE＋392 DATA bytes／12,195 指令／0 具名 UND**；APP 的 159 個 C/H 檔及 **95.54% 靜態 byte 覆蓋率**不變。4-byte 啟動來源缺口與硬體、Flash、OTA 相容性仍未解決，**尚不可宣稱可燒錄**。

可考慮新增離線 callback 來源與旗標／清除路徑診斷；尚未實作 UI 或硬體控制。

```sh
python experiments/tsl9-resident-callback-slot-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
