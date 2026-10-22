# NV 寫入 callback 與 timer：真實 C/C++ 原生重建

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

此輪從原始 ID2966 FW 實際重讀六個 source groups，**294B／115列**，包含寫入 callback 0x197BE..0x197F0、timer 0x19764..0x1979A 與四個實際 flash leaf。重建可讀 C11/C++17，沒有把原始指令當 opcode 模板，也沒有 HOST interpreter 或 target 執行。

new C 檔普通 include 已封存的 flash-entry-order/src/flash_native.c/native_io.h，六個真正 helper 定義全部保留。只用 noinline 前置宣告保留清楚的 C call 邊界；既有函式本體沒有修改。新 timer 的演算法是普通 volatile C，只有沿用既有 native-clock 模式的最小 `mv output,gp` 讀取橋接，不設定 GP，也不提供常數 GP。

## 寫入呼叫流程

輸入為 A0=destination、A2=source；entry A1 不使用。正常完成依序呼叫實際 C 定義：

1. unlock(original destination)
2. erase(original destination)
3. program(original destination, source)
4. lock(program 正常 A0 結果)
5. delay(1)，然後 wrapper 返回0

沒有在此流程新增 status(49) 或 CSR mask，結果0也不是硬體狀態。真正 program helper 仍會向256-byte window 寫入64個 WORD，來源讀取與目標寫入交錯、每個來源 WORD 重新讀取，沒有預先緩衝。兩個未被新 wrapper 使用的 genuine status／quarter 函式仍完整列入物件；quarter 既有的 status49／CSR136 只屬於其原本程式碼。

原始 program 呼叫邊界還有 A2=從 frame 新讀取的 source；typed program 的兩參數投影只在「callee 不讀該 entry A2，之後自行設定256」條件下涵蓋正常效果，不是原始完整實體入口狀態。

## Timer 的精確位址效果

保持原始數值位址，不推測時間單位或硬體欄位名稱：

1. fresh R32(E000F004)，W32(E000F004, value&~1)。
2. fresh R8(uint32(GP+382))，乘完整 incoming A0，uint32 回繞。
3. 把乘積 W32(E000F010)，W32(E000F014,0)。
4. 兩次分別 fresh R32(E000F000)，依序 OR16、OR33 後寫回。
5. 每次 fresh R32(E000F004)，反覆等到 bit0 **SET**。
6. fresh R32(E000F000)，AND~1 後寫回，正常 A0 保留輸入。

poll 無 timeout，不能宣稱必定返回。最少12個 target accesses；不是13，也沒有把兩次 CTRL read 合併或把初始 +4 改成 +0。offset16／20 只是本輪採用的數值描述，沒有新增 counter 語意。

## 真正編譯結果與限制

| genuine global FUNC | bytes／指令 | 說明 |
| --- | ---: | --- |
| status 18E90 | 8／3 | 新流程未使用 |
| unlock 18E98 | 30／10 | 額外 own-written A1 |
| lock 18EB6 | 14／6 | 真實 C helper |
| erase 18EC4 | 46／19 | 額外 own-written A1 |
| program 18EF2 | 100／38 | 真實64次 WORD 迴圈 |
| quarter 9C0A | 64／23 | 新流程未使用 |
| delay 19764 | 60／23 | 無 frame，own-written A1/A2 |
| write callback 197BE | 72／26 | 16-byte frame、五個真實 C call |

C/C++ 所有函式機器碼一致。完整 ET_REL 是 **394B／148指令／8 globals、UND=0、RELA=10、ABS provider=0**。五個 R_RISCV_CALL_PLT 屬於新 callback；另五個 genuine JAL relocations 屬於既有 quarter。它們仍待真實 linker 解 relocation，沒有宣稱 ET_REL 能直接執行或已配置到原位址。

原始 write 是50B／20列、32-byte frame；新 write 是72B／26列、16-byte frame，使用並保存 S0/S1。原始 source 先存到 frame，再於 program 前重新讀取；新 C 保存在暫存器。正常效果投影需要有效私有 stack，且 frame/source/destination/MMIO 無不利 alias。

原始 timer 只寫 A2/A3/A4/A5，正常 A1 保留 source、A2 是乘積。新 timer 額外寫 A1，結尾 A1=E000F000、A2=最後 fresh E000F000&~1；A3/A4/A5 也不是原始固定出口值。新 write 因此沒有原始完整 register ABI。新 unlock/erase 的 A1 寫入與 retained quarter 既有 inline-ASM clobber 宣告也必須獨立審查；「使用標準 C call」不代表原始次要暫存器結果相符。

完整 ABI、fault/IRQ/async、原始 frame 觀察、固定配置及 installed provider 均未證明。不調 flags 追暫存器，不用假 provider／stub／ABS，不 link，不產 BIN，不刷寫。程式含真實 Flash/MMIO 操作，**不可在 HOST 或硬體執行本輪產物**；此輪完全未執行 native、CPU/ISA/ESIL、MMIO 或 HOST matrix，也沒有網路操作。

## 入口與證據

```sh
sh experiments/tsl9-nv-write-callback/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE 支援 workspace apk-analysis/tsl9-v4160-nv-write-2026-10-22 與交付 analysis/v4160-nv-write-2026-10-22。NEW 必須是 model/build 內尚不存在的目錄，省略使用 UUID。W artifacts 是 build/native-v1/{c,cpp}；保留真實 object、完整 IR/disassembly、六項 MD inputs、工具/resource header hash、所有 logs、relocations 與 receipts。check 預設只讀來源/metadata；顯式 receipt 才讀實際產物，絕不重編或執行。provenance 或 check --firmware 才重讀原始 FW 六個範圍。

Python/sh 原始碼可跨平台；此輪 native 結果限定既有固定 Windows NDK hash。sh runtime 維持未驗證，沒有重試先前被拒的 Git Bash。新文字為 LF、單一 EOF newline，封存前做 Git 式空白檢查；既有來源及真實 compiler raw logs 原樣保留。兩個 original-*.bin 只是50B／54B的原始來源證據，不是重建 image。

原始 source capture 起初使用較窄舊 decoder，遇1977E 的 ORI 明確拒絕；改用已封存 binding-review 的完整 decoder context 才建立來源證據。此事發生於第一次 native compile 之前，沒有改 C/flags 或增加原生配方；來源擷取錯誤摘要保留在 build/source-capture-history。

獨立 raw review 確認 retained quarter 的通用 inline-ASM clobber 宣告沒有列出 unlock/erase 實際寫入的 A1；目前有限機器路徑在 SP+12 保存 source 並於 erase 後重讀，因此未觀察到該路徑的 live-A1 反例。這不表示其通用 ASM contract 或原始完整 ABI 已獲核准。
