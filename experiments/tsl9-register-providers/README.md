# Register 讀寫與接收鏈（離線 C/C++）

[English](readme.en.md)

重建原廠 ID2966 V4.1.60 的 `16994..169DC` read72B／26指令與 `16A30..16A7C` write76B／28指令。三個SPI呼叫以外，分別60B／64B與原廠一致；原32B frame、兩個獨立GPIO條件、fresh參數槽位及RA讀回順序保留。

read依序傳3／fresh A1／0；write依序傳2／fresh A1／fresh A2。兩者都先讀回RA，再以32-bit寫入`40010810=17`，最後回傳第三次SPI留下的A0，並非固定0。GPIO選擇寫入為`40010814=16`／`1`；channel3兩次都做，channel0仍做SPI與清理。

實際280B ET_REL整合consumer62＋receiver70＋read72＋write76。十二個JAL relocations保留：四筆指向真正重建的內部FUNC，八筆仍指向SPI／packet兩個UND providers。**這是連結結構證據，不是已解析執行碼或可燒錄BIN。**

```sh
python3 experiments/tsl9-register-providers/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-register-providers/build/my-check
```

`LLVM_BIN`指向既有RISC-V LLVM，`my-check`須尚未存在；以`--replay`取代`--build-root`可重播本機收據。`--require-firmware-ready`必須拒絕。C11／C++17使用明示GNU暫存器／組語架構埠；不下載工具、不執行RV32／MMIO、不產生或燒錄BIN。

SPI／packet／installed resident與完整IRQ／fault／實體硬體／OTA仍未閉合。read的隱式A1槽位捕捉與A0殘值屬固定編譯配方下的架構埠證據，不是任意編譯器的C保證。公開收據以可攜路徑產生，本機原件保留；診斷功能仍只記錄候選。
