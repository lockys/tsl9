# BLE 初始化複製後的預設值與 callback 邊界

[English](readme.en.md)

兩份保留候選的初始化函式都完整讀取 **228 bytes／92 條指令**：V1.40 為 0x43D0A..0x43DEE，V1.31 為 0x43C7E..0x43D62，右界不含。這些仍是條件式參考實作，尚未證明存在於原機 ROM。

## 已確認的來源

原來無法解碼的指令屬於條件式 Xwchc `QK_C_LBU`。其 operand 位元依保留且有 SHA-256 的 TableGen 文件解析；radare2 對這些 bytes 的浮點標籤不能當作正確語義。

64-byte copy 返回後，A5 被設為 live S0 加上配置偏移。至第一個 callback 前，共八個預設值寫入：配置 +12 的 halfword、+14 的 byte、+16 的 halfword，以及 +15、+18、+19、+20、+22 的 byte。它們皆避開 `staCB` 的 +52..55；這個區間沒有其他 call，也沒有 S1 的明示改寫。+22 的檢查從 live S1 讀取，而非從配置副本讀取。

下一個呼叫從配置 +44 新鮮載入函式指標，零值則略過；非零時於 V1.40 的 0x43DC4／V1.31 的 0x43D38 呼叫。依相同 header 順序與既有 RV32 layout，此欄位推論對應 `tsCB`／temperature；本輪沒有新增 offsetof44 編譯證據。原 App 實際 0x19A92 的 AUIPC、0x19A96 的 ADDI -674，以及 0x19A9E 的 SW SP+60，將數值 **0x197F0** 存入 App config+44。這只證明該次設定來源，仍須保持原來的 mapped-copy／無干擾等前提，才可連到 callback 的實際目標。

0x197F0 的初始靜態觀察包含 128-byte frame、ADC/MMIO 存取與 nested call，這些效果尚未在本範圍證明。初始化還會於 V1.40 的 0x43DD8／V1.31 的 0x43D4C 呼叫 0x43BCA／0x43B3E。不能把預設值區間的無重疊結果延伸為整個初始化或 callback 執行期間的零值保證。

## 驗證與限制

```sh
python analysis/v4160-resident-memory-2026-10-22/continuation-review/check.py --project-root .
python analysis/v4160-resident-memory-2026-10-22/continuation-review/check.py --project-root . --candidate-root /path/to/retained-reference --firmware /path/to/ID-2966-V4.1.60-decoded.bin
```

預設僅核對 metadata 與封存檔；第二個命令才讀兩份候選與原 App。實檔模式核對完整來源、原 App callback 設定的 42 bytes，並拒絕六個維持指令形狀、只改一個 operand 的有效原始 byte 反例，分別改變預設值 load／store 偏移及 callback 欄位偏移。

`ledger.json` 列出全部 typed rows、bytes、雜湊與反例。這是靜態來源／區間核對，沒有執行 CPU 狀態、RV32、ISA 模擬、MMIO 或實機；沒有新增 provider／BIN，也不證明 installed ROM、IRQ、Flash/NV 或 BLE OTA 相容性。
