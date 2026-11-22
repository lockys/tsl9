# IRQ 39：reset 到 APP 入口的中斷狀態

接續 [IRQ 39 啟用順序](v4160-irq39-enable-order.zh-TW.md)。原 APP 在設定 `mstatus` 和 `mtvec` 後呼叫 `0x1874a`。該時鐘函式的 93 條指令沒有 SYSTEM 指令或子呼叫。它不是保證返回的直線程式：`0x18806` 等待基址 `0x40021000` 的 bit 25 變成 1，`0x18824` 等待基址 +4 的 bits 3:2 等於 2。若走到這兩處，停留多久取決於外設。正常返回後，`0x1872c` 寫 `mepc=0x9008`，`0x18730` 跳到 `0x40000`，不會順序執行其後的 `mret`。

對 V1.31 **參考**入口、初始化器和兩段搬到 RAM 的 helper 原碼，按指令邊界核對 67 條；唯一 SYSTEM 是 `0x6debe` 的 `mret`。依標準機器模式返回語意，MIE 取自返回前的 MPIE，不是保留返回前的 MIE。若初始設定有效、時鐘與複製都正常完成、RAM 執行的確是所核對內容且無陷阱或其他介入，則返回 APP `0x9008` 時 MIE 應為 1，`mtvec` 仍為 `0x803b`。只用現有 HEX 無法跑完這條路：第二次複製最後一個來源 word `[0x6eb2c,0x6eb30)` 缺失；這既不是零值證據，也不是實機故障證據。

重現：`python analysis/check_v4160_irq_handoff.py <原始 APP BIN> <V1.31 參考 carrier BIN>`（另以 `-O` 重跑）；`python scripts/check-rf-3538-init.py` 核對 HEX 缺口。檢查器固定兩檔 SHA-256，只計所列視窗中的 SYSTEM 編碼，不模擬中斷、CSR 或時鐘。尚未證明從 `0x9008` 到主迴圈的所有呼叫維持上述狀態。
