# NV read：保留未移位的 count
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本元件延續 [30B／14指令候選](../tsl9-nv-read-registers/README.md)，以 genuine C 的32-bit左移與最小暫存器／呼叫 ports，消除原先暫時移位 A1 再搬至 A2 的差異。整理後來源是 [src/native/nv/nv_read_live_count.c](../../src/native/nv/nv_read_live_count.c)。

## 本輪實測

C11／C++17 的 object 與 linked 元件均為 **30B／13指令**，code SHA256 `05b184cb6e192355342a6b6e71a7db136f2d53aa7aa33a341fb1551f4b49f58a`。原版亦為30B／13指令，但**整個函式仍不相等**。原版 SHA256 為 `e9e2a0f4b50184fa5c7b37ee004867f393b8c960fe9e66e81dc40af897114f62`。

相對函式起點的 `[12,22)` 共10B，包含 `SLLI A2,A1,2 → MV A1,A0 → MV A0,A4 → JALR A5`，逐 byte 等於原版。wrapper不新增A3寫入，不把RA當來源scratch，移位前不再破壞A1。callee仍可能修改其宣告的caller-saved暫存器。

原本的空ASM固定A2邊界只限制shift結果最後在哪裡，不能約束前面的C計算。新port以真實SSA依賴要求：先保存destination到A4，再保留未移位的A1，才計算C shift並交給A2。ASM不執行shift、不攜帶複製的原函式、不提供fake provider。word-count高位回繞仍保留。

每次呼叫仍fresh READ32(0x4004C)，呼叫前A0=entryA2、A1=entryA0、A2=u32(entryA1<<2)、A4=entryA2、A5=fresh slot value。未知provider若未正常返回，不虛構回傳零。

## 尚未閉合

- 原版先讀slot才配置frame並保存RA；候選先配置frame／保存RA再讀slot。A4搬移相對RA保存的順序亦不同。
- 原版先還原RA才令A0=0；候選先令A0=0。
- slotword及其installed provider身分、完整ABI、fault／IRQ／stack alias、ROM、啟動與原硬體相容性未證。
- static UND／RELA／global ABS均為零，不代表動態provider已知。30B大小相同不代表可直接放進原硬體。

## 可重播的離線驗證

從專案根目錄，使用明確的原BIN、既有LLVM及全新build目錄：

```sh
python3 experiments/tsl9-nv-read-live-count/verify.py --project-root . --tool-dir "/absolute/LLVM/bin" --firmware "/absolute/ID-2966-V4.1.60-decoded.bin" --build-root "/absolute/project/experiments/tsl9-nv-read-live-count/build/new-run"
python3 experiments/tsl9-nv-read-live-count/verify.py --project-root . --replay "/absolute/project/experiments/tsl9-nv-read-live-count/build/component-v2/c/verification.json"
```

Windows可使用 `py -3`／`python`。實測工具為Windows Android NDK27.1.12297006／LLVM18；verifier固定工具、stdint、來源、linker、原始BIN及operand ledger hash，並核對實際MD依賴、IR值流、完整ELF配置與LLVM raw readback。其他平台未實機測試。這些靜態檢查不執行ISA／MMIO，也不是獨立CPU語意證明。

最終收據位於 `build/component-v2/{c,cpp}/verification.json`。早期native-v1只有保留原A1，編譯器改用A3 scratch並增為32B，因此未採用；其來源snapshot保存在該build目錄。native-v2加上A4→A1先後依賴後才得到本次結果。component-v1的C++ `noundef` IR解析失敗保留；解析器精確接受該限定後component-v2通過。舊輸出屬歷史快照，不宣稱可由新版verifier重播。

本輪未產生新OTA BIN、未刷寫、未操作原硬體。
