# ROM 流程依賴與狀態回呼重建

[English](readme.en.md)

已接入 [C/C++](../../src/native/receive/rom_dependencies.c) 的七個完整函式，**422B／153條指令、55個原始區塊、42個控制轉移與一組回呼位址參照**。接通9792、9FC2、A2EE、ABF2，並包含必要的81DE、A204及9F74完整路徑。

| 完整原始範圍 | 大小 |
| --- | --- |
| `81DE–81EE` | 16B / 6i |
| `9792–979E` | 12B / 5i |
| `9F74–9F7A` | 6B / 2i |
| `9FC2–9FC8` | 6B / 2i |
| `A204–A2EA` | 230B / 81i |
| `A2EE–A37C` | 142B / 54i |
| `ABF2–ABFC` | 10B / 3i |

C11／C++17元件相同：**15654B code＋674B data、5457條指令、1048 RELA、79 UND**。先前15232B code及674B data保留；四個舊依賴接通後展開10816、B6EA、D05C三個新依賴，因此80→79。原生連結器配置後，所選 **16328B** 與官方BIN原址逐byte一致；仍是entry=0、無PT_LOAD的診斷ELF，**不能燒錄**。

已確認的靜態邏輯：9792依完整A0是否為零選擇2或250，再尾跳9454；9FC2 fresh讀GP+172的byte；ABF2在原始PC讀2000BEE0的byte。81DE讀取設定指標+5的byte，執行低2位遮罩再加1，保留1–4值域，沒有自行縮減選項。

A2EE保留原16B frame及所有尾跳／RET。符合原條件時，GP+176以(old+1)&3更新、GP+175設1，將9F74位址與低32位輸入×1000傳向9124；9F74會清零GP+175。A204完整230B包含GP+178／179／180狀態讀寫、40038表項的間接呼叫及分支，未以預設行為取代未知尾端。計時單位、動作碼及實體功能仍未知；位址傳遞沒有證明回呼已註冊或執行。

[原始指令](evidence.json) · [結果、欄位與雜湊](summary.json) · [79個待完成提供者](next-providers.json) · [整合器](../../experiments/tsl9-rom-dependencies/integrate-v1.py)

來源集105個C/H、78個code units及1個獨立資料單位，共158組比對／316物件。舊154組結果與925筆產物記錄保留。917個直接轉移中838個指向實際指令，79個仍為未實作參照；5009個普通順序位置與317個可能call-return位置皆有指令。261個暫存器間接轉移、10個MRET及8034 EBREAK後續仍未證，沒有宣稱完整CFG。

下一步追10816、B6EA、D05C。新功能候選為**離線狀態計數器與回呼參數檢視**，目前僅提案；先顯示原值、位址及未知單位，不改硬體控制。

實體MCU、RAM／ROM、私有ABI、非同步狀態／IRQ與OTA仍未證。未執行目標、HOST模型或ISA模擬，未連網或接觸硬體，未產生BIN或commit／push；歷史個資問題尚存。

```sh
python3 experiments/tsl9-rom-dependencies/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-rom-dependencies/build/component-v1
python3 experiments/tsl9-original-layout/build-v11.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/rom-dependencies-v1
python3 experiments/tsl9-original-layout/verify-flow-v10.py --replay experiments/tsl9-original-layout/build/rom-dependencies-flow-v1
```
