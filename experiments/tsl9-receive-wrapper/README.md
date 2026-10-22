# 接收入口與旗標消費鏈（離線 C/C++）

[English](readme.en.md)

重建原廠 ID2966 V4.1.60 的 `16B0A..16B50`，共70B／26指令：讀 register `2C`，分別處理 `61`／`71`，最後恢復 frame 並尾跳寫入 `2C=0`。第一個下游呼叫後依原碼使用當下的實體 S0／S1；不假設未知 resident provider 保值。

入口14B緊接主體56B。四個 JAL 視窗外54B與原廠相同；四個呼叫／尾跳保留三個真實 UND providers。另一個實際 ET_REL 產物將上一輪62B旗標消費函式與此70B入口放入同一132B區段，連結到真實函式定義；relocations仍在，不能當作已解析執行碼。

原16B frame及fresh saved-slot reads保留。RA／SP／S0／S1為架構埠專用；S0保存與mask0x02判斷／分支使用明示組語埠，避免LLVM18額外保存callee-saved暫存器。其餘條件、參數與呼叫流程為C。這不是pure C第二個bit判斷實作，也不宣稱一般C ABI。

```sh
python3 experiments/tsl9-receive-wrapper/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-receive-wrapper/build/my-check
```

`LLVM_BIN` 指向既有RISC-V LLVM；`my-check`須尚未存在。以 `--replay` 取代 `--build-root` 可核對本機收據；`--require-firmware-ready` 必須拒絕。不下載工具，不執行RV32／MMIO，不產生或燒錄BIN。

尚缺下游SPI／接收封包／installed resident實作與完整ABI、主迴圈／IRQ／實體硬體及OTA相容性。早期frame失配試驗留在本機，未納入`src/`。
