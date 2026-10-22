# 初始化的五筆寫入：9F4C

[English](readme.en.md)

這個完整函式位於官方 ID2966 V4.1.60 的 `[0x9F4C,0x9F74)`，由初始化鏈 `0x9260` 呼叫。可讀 C 與 C++17 使用相同來源，MMIO 使用真正的 `volatile uint32_t`；空暫存器 port 保留前面三條指令的形成順序及正常 A4／A5 出口，不包含 opcode carrier。

| 次序 | 位址 | 32-bit 值 |
| --- | --- | --- |
| 1 | `0x40003000` | `0x5555` |
| 2 | `0x40003004` | `3` |
| 3 | `0x40003008` | `1500`（十進位，`0x5DC`） |
| 4 | `0x40003000` | `0xAAAA` |
| 5 | `0x40003000` | `0xCCCC` |

正常出口 A4=`0xCCCC`、A5=`0x40003000`，其餘 GPR、GP、SP、RA 不改。原函式沒有讀取、call、frame、CSR、fence 或 poll；接著 `0x9F74` 立即是另一個 6-byte 函式，不能擴大覆蓋範圍。

## 驗證與使用

在專案根目錄指定既有本機工具：

```sh
python3 experiments/tsl9-init-write-sequence/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --build-root experiments/tsl9-init-write-sequence/build/my-run
python3 experiments/tsl9-init-write-sequence/verify.py --project-root "$PROJECT_ROOT" --tool-dir "$LLVM_BIN" --replay experiments/tsl9-init-write-sequence/build/my-run/c/verification.json
```

Windows 可用 `py -3` 及 PowerShell 的 `$env:PROJECT_ROOT`與 `$env:LLVM_BIN`。新 build 目錄必須不存在。此工具不下載依賴，也不執行／模擬 RV32、MMIO 或操作硬體。

初次 C 候選雖為40B，前三條指令的順序不同，保留在本機 `build/probe-v1`；以明確空 port 修正後，`build/probe-v2` 的 C11／C++17 object 與 linked function 都逐 byte 等同原始40B／15指令。不是只比較 store 數值或宣稱局部等價。正式收據與公開摘要另見 [分析目錄](../../analysis/init-write-sequence-2026-10-23/summary.json)。

**這不是完整韌體。** 寫入模式僅能作為周邊作用的候選線索，不能據此確認晶片、暫存器意義或 timeout。完整main／resident／vector／IRQ與原機 RAM ownership、OTA相容性仍未證。診斷 ELF 固定在原函式位址只供靜態比對，不產生韌體 BIN；`--require-firmware-ready` 必須拒絕。

工具使用專案內固定 SHA256 的官方 BIN，沒有 `--firmware` 參數；正式本機收據為 `build/verified-v3/{c,cpp}/verification.json`。每語言 13 項負例、4 個實際 recipe、2 個實際 ELF；ABS provider 為零，編譯器 local ABS metadata 另外列明。
