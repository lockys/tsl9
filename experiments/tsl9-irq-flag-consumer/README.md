# IRQ 旗標消費函式（離線 C/C++）

[English](readme.en.md)

重建官方 ID2966 V4.1.60 的 `0x17002..0x17040`：先清除 GP+360 的 bit0／bit1，再以 channel 1／2 呼叫接收流程。每次呼叫後清除當時 GP+361／+362；第二次判斷重新讀取旗標，不快取第一次結果。

原碼為 62 bytes／21 指令。候選入口 8 bytes 緊接可讀 C 主體 54 bytes；實際 ET_REL 部分連結檢查相鄰關係。兩個真實 `R_RISCV_JAL` 呼叫保留未解決，其餘 54 bytes 與原廠一致。**這不是完整 62-byte 已解析碼相等，也不是可燒錄 BIN。**

保留原本 16-byte frame、先 LBU 再保存 RA 的順序、呼叫後 fresh GP／RA slot 與 A0 殘值。RA／SP 為架構埠專用且須使用記錄的固定暫存器旗標；不能當成一般 C ABI 函式呼叫。

```sh
python3 experiments/tsl9-irq-flag-consumer/verify.py --project-root . --tool-dir "$LLVM_BIN" \
  --build-root experiments/tsl9-irq-flag-consumer/build/my-check
```

`LLVM_BIN` 指向既有 RISC-V LLVM 工具目錄；`my-check` 須為尚未存在的目錄。不下載工具、不執行 RV32 或 MMIO。實際收據路徑由驗證器回報；以 `--replay` 取代 `--build-root` 可重新核對原始本機收據，`--require-firmware-ready` 必須拒絕。

尚缺 `0x16B0A` 及下游接收／SPI／resident provider 重建與 ABI 證據，也未證明完整 IRQ、實體硬體或 OTA 相容性。公開收據使用可攜路徑；保留原始收據於本機。
