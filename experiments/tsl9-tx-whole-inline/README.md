# TX 原址連續重建（離線研究）

`tx.c` 將原先獨立的 prefix 與 loop 連成一個 section，補上 `0x8a56` 開頭、兩個 gate 和 `0x8b6c` 的 early return；完整 `[0x8a56,0x8b6e)` 280 bytes。使用具名標籤、RISC-V 指令及 `.insn` ISA 欄位，無 raw bytes、填充或 incbin。這是裸函式的指令級重建，不是可攜 C 邏輯，也不應呼叫或刷寫。

NDK 27.1.12297006 LLVM、RV32IMAC、關閉 relaxation、連結在 `0x8a56`：C11 與 C++17 各 280/280 bytes 相同，物件無 relocation。固定本機標示 decoded 參考 76800 bytes，`[0x8a56,0x8b6e)` SHA-256 `3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b`；並非來源或簽章認證。獨立解碼八條 B 分支及 `0x8b6a` C.J 的目標。兩語言各測上限指令、early 分支條件、early 分支目標及 loop 後跳目標 mutation，確認逐 bytes 不同；兩個目標突變另解碼為 `0x8b6a`、`0x8b0c`。參考截短與單 byte 變造被拒絕，並非窮舉。

## 邊界及外部入口的證據範圍

`0x8a56` 有長度檢查及正常 frame prologue；`0x8a5a` 直接分支到 `0x8b6c` 的 `ret`，而 `0x8b6a` 是 loop 後跳，`0x8b50` 是間接 tail jump，故 early return 並非 tail jump fallthrough。這些與一個以 `0x8a56` 開始、含 `0x8b6c` 的函式相符，但單靠 bytes 不能證明原始符號大小或排除其他入口。另一次對同一映像的半字 raw sweep 到 `0x8a56` 九個直接 JAL/C.J/C.JAL 編碼（含 `0x13b80` 及 tail edge `0x13eac`）；raw sweep 有資料/重疊指令假陽性且不涵蓋 JALR、間接表或中途入口，**不能宣稱外部入口已完整枚舉**。此研究也沒有建立來源語言、ABI、動態可達性及硬體行為。

```powershell
$llvm = "$env:LOCALAPPDATA/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin"
$ref = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
python experiments/tsl9-tx-whole-inline/verify.py --tool-dir $llvm --reference $ref
```

所有編譯輸出只存在自動清除的系統暫存目錄；未替換候選、產生完整映像、執行韌體、OTA 或刷寫。byte 一致不是可刷寫或安全證據。
