# NV write：修正真實 quarter call 的 compiler clobber contract

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

新 profile 只補上兩個實測缺少的 A1 clobber：FN_CALL_UNLOCK 與 FN_CALL_ERASE。先普通 include 舊 flash_native.h/native_io.h，利用 include guards 保留舊定義，再 undef/redefine 這兩個巨集，最後普通 include 已封存的 NV-write C。所有演算法、八個真正函式與原 compiler flags 不變；舊來源、seals、objects 及 images 都沒有修改。

**實際 C11/C++17 編譯及唯讀 replay 通過：八個函式的 raw code、大小、own-written registers、十個 relocations 全部與原物件相同。** 完整 ET_REL 仍為394B／148指令／8 globals、UND=0、RELA=10、ABS provider=0。修正發生在 compiler-call 宣告；目前這個編譯 profile 的機器碼沒有改變，不代表原先通用宣告正確。

## 五個真實 callee 的覆蓋檢查

從實際 object 的全部 raw instructions 推導 own-written GPR，再解析實際 LLVM inline-ASM 的 output、input-only、clobber：

| callee | 實際自身寫入 | 舊宣告缺漏 | 新宣告 |
| --- | --- | --- | --- |
| unlock | A1/A3/A4/A5 | A1 | 全部覆蓋 |
| status | A5 | 無 | 全部覆蓋 |
| erase | A0/A1/A3/A4/A5 | A1 | 全部覆蓋 |
| program | A0/A2/A3/A4/A5/A6 | 無 | 全部覆蓋 |
| lock | A3/A4/A5 | 無 | 全部覆蓋 |

每個 call 都保留 RA link 與 memory clobber；program 的 input-only A1 由實際 callee 不寫 A1 證明。不是因為採用標準 C 或 PSABI 就假設暫存器可以破壞。只有五個 call 的全部實際寫入均被覆蓋時，才回報本 profile 的 compiler-call contract repaired=true。

完整 LLVM IR 對照只忽略 ModuleID、source_filename 與 !srcloc source-location annotations；其餘相同，只有 unlock/erase 新增的兩個 ~{x11} 不同。八個函式（包含未被新 write 使用的 genuine status／quarter）完整保留，沒有假 FUNC、stub、ABS provider 或 opcode carrier。

quarter 目前仍是64B／23指令、32-byte frame；write 仍72B／26指令、16-byte frame；timer 仍60B／23指令。這輪不修 timer 的 A1/A2 出口、原始 write frame／source reload 差異、fault/IRQ/async 或不利 alias。原始完整 register ABI、installed provider、固定配置及硬體驗證仍為 false。

## 真實 baseline 與可攜 replay

每個語言的 baseline folder 必須含實際舊 native.o 與 native.ll，**不讀取或 replay 舊 verification.json**。物件必須精確符合已實讀的 SHA256：

`b30c679bd1e15a7a59be59b4ed723a6f98f78cc022e93e314e4c59f85c7aa09f`

baseline-facts.json 保留從真實舊 object 推導的每函式 code hash／written GPR／relocations 與每種語言的 normalized IR hash。新 build 把實際 baseline 物件及 IR 複製到 mode/baseline/native.o、mode/baseline/native.ll，再以真正 objdump 讀取並逐函式比較；replay 只需要這份本機 archive，不需要原 baseline folder 或 W 的舊 receipt。

```sh
sh experiments/tsl9-nv-write-call-contract/verify.sh --project-root ROOT --tool-dir LLVM --build-root NEW --baseline-c-folder OLD_C --baseline-cpp-folder OLD_CPP
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

CASE 支援 workspace apk-analysis/tsl9-v4160-nv-call-contract-2026-10-22 與交付 analysis/v4160-nv-call-contract-2026-10-22。NEW 必須是 model/build 下尚不存在的目錄；省略時用 UUID。W baseline folder 省略時使用目前 root 的舊 model/build/native-v1/{c,cpp}，D/P 應傳入已驗證的實際 baseline folders。正式 W 結果是 build/contract-v1/{c,cpp}。

新 receipt 保留 mode/source_pins/tools/artifacts/commands，完整 MD 七項輸入、IR、兩份物件的完整反組譯、實際工具/resource hash 與全部 raw logs。預設 check 只驗 source/metadata；顯式 receipt 才讀實際 object/IR，不編譯、不執行。靜態 classifier 沿用已驗證的兩個舊檔及其相對 import hierarchy；交付樹使用 canonical analysis/function-hardware/fifty-fifth-round、fifty-seventh-round。

只使用一個來源 overlay／compiler recipe，沒有 flag search 或編譯失敗重試。沒有 native、CPU/ISA/ESIL、MMIO、HOST、硬體、網路或 vendor 操作，也沒有 link／BIN。新文件為 LF、單一 EOF newline；README 與繁中版本相同，英文另存。sh runtime 沒有重試先前被拒的 Git Bash，仍未驗證。
