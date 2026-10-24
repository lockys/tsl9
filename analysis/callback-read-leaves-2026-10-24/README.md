# Callback byte 讀值入口重建

[English](readme.en.md)

已將 **11 個完整 getter，94B／29 條指令** 接入 [C/C++ 來源](../../src/native/receive/callback_read_leaves.c)。每次執行 LBU 後以 A0 返回；保留原始 AUIPC 或 live GP 讀取方式，沒有固定假回傳值或新增依賴。

原生 C11／C++17 元件相同：**14618B code＋674B data、5078 條指令、961 RELA、80 UND**。先前14524B code及全部674B data保留，11個原本未解析的符號現在指向真實函式。原生連結器配置後，所選 **15292B** 與官方 BIN 的原始位址逐 byte 一致；仍是 entry=0、無 PT_LOAD 的診斷 ELF，**不能燒錄**。

| 原始入口 | 靜態讀取地址 | 完整大小 |
| --- | --- | --- |
| `181C4` | `0x2000C925` | 10B / 3i |
| `8440` | live `GP + 364` | 6B / 2i |
| `B1B0` | live `GP + 196` | 6B / 2i |
| `C35A` | `0x2000BF12` | 10B / 3i |
| `CD44` | `0x2000BF26` | 10B / 3i |
| `F6B0` | `0x2000BF9D` | 10B / 3i |
| `F6E2` | `0x2000BF9F` | 10B / 3i |
| `F714` | `0x2000BFA2` | 10B / 3i |
| `F746` | `0x2000BFA4` | 10B / 3i |
| `FA2A` | live `GP + 278` | 6B / 2i |
| `FA36` | live `GP + 279` | 6B / 2i |

PC 相對地址僅在各入口置於原始 PC 時成立。GP 項目保留當下 GP；不假設執行時 GP 值或實體記憶體有效性。181C4 在13450、13462被分別呼叫；後續移位／遮罩將兩次fresh讀值組入不同位元，不能當成一致時間點的快照，也還不能命名欄位用途。

[原始指令](evidence.json) · [結果與雜湊](summary.json) · [80 個待完成提供者](next-providers.json) · [整合器](../../experiments/tsl9-callback-read-leaves/integrate-v1.py)

來源集為102個 C/H、75個code units及1個獨立指標資料單位，共152組來源比較／304物件。舊148組結果及889筆產物記錄相同；凍結檢查器未改。836條直接轉移中756條指向已編譯指令，80條仍為未實作的原址參照。4663個普通順序位置與292個可能call-return位置皆有實際指令；237個暫存器間接轉移、10個MRET及8034的EBREAK後續行為仍待證明，沒有宣稱完整CFG。

其餘9個callback待完成入口只保留48B窗口，未截斷為完整函式。D1A8 的窗口顯示 AUIPC／ADDI／RET 指標返回，與byte讀值種類不同；下一輪先核對其完整入口，再追16DAC與寫入端。

可新增功能候選：**離線狀態欄位檢視器**，顯示地址及已知位元組裝證據；尚未實作，不改變原機控制策略。欄位語意、GP／RAM所有權、非同步狀態、原機啟動／ROM／IRQ與OTA仍未證。未接觸硬體或網路、未產生BIN、未commit／push；歷史個資問題未清除。

```sh
python3 experiments/tsl9-callback-read-leaves/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-read-leaves/build/component-v1
python3 experiments/tsl9-original-layout/build-v8.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/callback-read-leaves-v1
python3 experiments/tsl9-original-layout/verify-flow-v7.py --replay experiments/tsl9-original-layout/build/callback-read-leaves-flow-v1
```
