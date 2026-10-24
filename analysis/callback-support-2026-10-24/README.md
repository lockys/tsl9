# Callback 指標與 payload 封裝重建

[English](readme.en.md)

已將兩個完整函式接入 [C/C++](../../src/native/receive/callback_support.c)：**D1A8 指標返回10B＋16DAC封裝40B，共50B／18條指令**。五個原始區塊保留真實分支、32B frame與呼叫，沒有替代回傳值。

C11／C++17元件相同：**14668B code＋674B data、5096條指令、963 RELA、78 UND**。既有14618B code與全部674B data保持原樣；新增16CC4呼叫指向既有真實實作。原生連結器配置後，所選 **15342B** 與官方BIN原始位址逐byte相同。產物仍是entry=0、無PT_LOAD的診斷ELF，**不能燒錄**。

| 原始入口 | 已確認的靜態邏輯 |
| --- | --- |
| D1A8–D1B2 | 返回 `0x2000BF48`，自身不讀取此地址。133A8呼叫後將指標放入A1、A2設19、A0設SP+60，再間接呼叫S0 |
| 16DAC–16DD4 | 若 `((A0-1)&255)>1` 直接RET；其餘路徑保留完整A0，以A1=SP+12、A2=2、A3=0呼叫16CC4 |
| 16DBA–16DCC | 建立32B frame，RA存SP+28，以SH zero將SP+12的2B清零，再真實JAL16CC4 |
| 16DCC–16DD4 | 恢復RA／SP後RET，或由條件分支直接RET；未截掉第二個出口 |

低8位條件不等於檢查完整A0為1或2；完整原值繼續傳給16CC4。19B資料的欄位語意、S0間接目標及實體傳送效果仍未知，不因長度猜成VIN，也不執行硬體命令。

[原始指令](evidence.json) · [結果與雜湊](summary.json) · [78個待完成提供者](next-providers.json) · [整合器](../../experiments/tsl9-callback-support/integrate-v1.py)

來源集103個C/H、76個code units及1個獨立資料單位，共154組比較／308物件。舊150組結果及901筆產物記錄保持一致。838個直接轉移中760個指向已編譯指令，78個仍是未實作參照；4678個普通順序位置及293個可能call-return位置皆有指令。240個暫存器間接轉移、10個MRET、8034 EBREAK後續行為仍未證；沒有宣稱完整CFG或實機等價。

下一步追171BA完整入口，以及2000BF48的寫入／使用端。新功能候選為**遮蔽識別資料的離線欄位配置匯出**，目前只有提案；不改變模組控制策略。

實體MCU、RAM／installed ROM、私有ABI、非同步IRQ與OTA仍未證。未執行目標／HOST模型／ISA模擬，未連網或接觸硬體，未產生BIN或commit／push；歷史個資問題尚存。

```sh
python3 experiments/tsl9-callback-support/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-support/build/component-v1
python3 experiments/tsl9-original-layout/build-v9.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/callback-support-v1
python3 experiments/tsl9-original-layout/verify-flow-v8.py --replay experiments/tsl9-original-layout/build/callback-support-flow-v1
```
