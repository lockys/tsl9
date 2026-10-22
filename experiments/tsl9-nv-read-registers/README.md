# NV read callback：保留原始暫存器介面

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

以可讀 C 與最小 register/call ports 改善 ID2966 V4.1.60 的 NV read callback。新來源已放入 [src/native/nv/nv_read_registers.c](../../src/native/nv/nv_read_registers.c)。這是獨立元件，尚未整合到 OTA BIN。

## 本輪改善與實物

舊 C 候選為32B／14指令，會把 A3 用作來源與 slot base 的 scratch。新 C11／C++17 均為 **30B／14指令**，wrapper本身不寫 A3，也沒有把 RA 當作來源暫存器。真正的 provider 仍可能改寫 A3；這個結論只涵蓋 wrapper 指令。

原版 `[0x1979A,0x197B8)` 是30B／13指令，SHA256 `e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62`。新元件SHA256 `55eaeff68d528f2e86c97ce41148fa5ef921bd325a35e86d439df5a1cc6dedda`，**不等於原版**。

C 本體進行 fresh volatile slot read 與32-bit左移，ports只處理固定暫存器及MOV／JALR呼叫邊界，沒有複製原始指令串或 provider stub。呼叫前：

| 暫存器 | 值 |
| --- | --- |
| A0 | 入口A2：destination |
| A1 | 入口A0：source |
| A2 | u32(入口A1 << 2)：byte count |
| A4 | 入口A2 |
| A5 | fresh R32(0x4004C) |

保留左移回繞；例如word count=0x40000000會得到byte count=0。原碼沒有null-target guard或count clamp，本元件也未新增。

## 明確未通過的部分

- 原版先讀slot，再配置frame，然後保存RA；目前先配置16B frame並保存RA，再讀slot。
- 目前先暫時改寫A1作左移，再搬到A2；A4設定的中間時序也不同。
- 原版先還原RA才令A0=0；目前A0先歸零。
- slot指向哪個原機provider及其完整ABI仍未知。static UND=0只表示沒有未解靜態符號，不能證明間接callee、正常返回或copy成功。

已審查的resident候選在null／zero-count early return會保留入口A3，所以去除wrapper新增A3對泛用邊界有意義；但該候選尚未證明是原機 installed provider。正常投影相同不能推成fault／IRQ／stack-alias等價。

## 離線驗證

在專案根目錄執行，明確指定原 BIN、既有LLVM與全新build目錄：

```sh
python3 experiments/tsl9-nv-read-registers/verify.py --project-root . --tool-dir "/absolute/path/to/llvm/bin" --firmware "/absolute/path/to/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/path/experiments/tsl9-nv-read-registers/build/new-run"
```

Windows可改用 `py -3`／`python`。本輪實測工具為Windows Android NDK27.1.12297006／LLVM18；工具與stdint hash必須符合本配方，其他平台未實測。

最新本機收據為 `build/component-v2/{c,cpp}/verification.json`。每語言的object與linked元件均只有一個30B FUNC／AX section，無額外配置、eh_frame、UND、global ABS或relocation。IR會核對實際source／count／destination／fresh target的SSA依賴與保守callee clobbers；固定candidate bytes與原始13列operand ledger支援指令註解，不宣稱另做ISA語意執行證明。

```sh
python3 experiments/tsl9-nv-read-registers/verify.py --project-root . --replay "/absolute/path/to/build/component-v2/c/verification.json"
```

早期native-v1保留RA/SP-reserved編譯錯誤；v2雖移除A3，卻新增RA scratch；v3的reserved-reg與opaque-callee clobber衝突被編譯器拒絕，沒有停用警告；修正call-boundary模型後v4使用標準配方。component-v1的C++ IR `noundef`限定解析失敗亦保留，verifier支援該限定後v2通過。舊輸出是歷史快照，不宣稱用新版verifier重播。

本輪未執行RV32／MMIO、操作硬體或產生韌體BIN。原硬體、ROM／BOOT、完整啟動／IRQ及OTA相容性仍未證明。
