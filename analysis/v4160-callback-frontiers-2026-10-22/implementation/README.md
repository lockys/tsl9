# NV 讀取 callback：條件式間接呼叫的 C/C++ 重建

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

已實際讀取 ID2966 V4.1.60 韌體，使用既有有限指令 decoder 重新解碼 **0x1979A..0x197B8 的30B／13列**，重建成可讀 C11/C++17。此輪只編譯及靜態讀取產物，沒有執行 callback、原生函式、CPU/ISA、MMIO、硬體或網路操作，也沒有重跑既有 HOST matrix。

公開介面 `tsl9_nv_read_callback_1979a(source,words,destination)` 是三個 u32 實體暫存器的條件式投影，不是已恢復的原始 C prototype。它每次真實 volatile 讀取 slot **0x4004C**，以實際載入值做真正間接呼叫：

```text
callee A0 = entry A2 (destination)
callee A1 = entry A0 (source)
callee A2 = uint32(entry A1 << 2) (byte count)
normal callback A0 = 0, ignoring the callee's normal A0 result
```

函式指標的三個 u32 輸入與 u32 正常結果，僅在該 slot 符合已封存 copy 候選的實際 register/效果投影時成立。原始 prototype、已安裝 slot→copy identity、callee 完整 ABI 均未證明；沒有以 SDK 名稱取代證據。載入值沒有被常數候選位址取代，沒有 fallback、stub 或假 provider。word count 以 uint32 左移，保留高位元回繞；callee 未正常返回時不會虛構 callback 回傳0或 cleanup。

## 實際原生結果

| 項目 | 原始來源 | 新 C 與 C++ |
| --- | ---: | ---: |
| 函式 bytes／指令 | 30／13 | 32／14 |
| 真正 global FUNC | 原來源範圍 | 1，無未使用 global |
| frame | 16B | 16B |
| own-written GPR | RA/SP/A0/A1/A2/A4/A5 | 再加 A3 |
| UND／RELA／ABS provider | 非 ELF 輸入 | 0／0／0 |

兩種語言的函式機器碼相同：SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`。實際 call 是 JALR RA,A5；完整有限 raw operand 解碼與 LLVM disassembly 同時保留。零 UND 不代表動態 slot target 已知或已驗證。

原始程式先讀 slot，然後分配 frame／保存 RA。新產物先 SP−16 並保存 RA 到 entrySP-4，再讀 slot；因此 slot fault 前的 stack/RA 效果時序不同。新程式先 LI A0,0 再還原 RA，原始則先還原 RA 再寫 A0,0，另一個 fault prefix 差異也保留。

新 A3 是暫存 entry source；原始 wrapper 沒有自行寫 A3。若實際 copy 候選在 no-loop 路徑沒有覆寫 A3，此差異可能持續到 callback 返回。沒有假設 caller-saved 暫存器都可任意破壞，也沒有把 A7/T bank 或 ambient A1/A2 視為無關。來源 C 的標準呼叫語法本身不構成原始 callee/caller ABI 證明。

實際 IR 是一次 fresh volatile slot read、shl i32 words,2、以載入 pointer 呼叫 destination/source/scaled-count，然後 ret i32 0。這個有限 call-boundary 投影不等於完整 fault/IRQ/async 或 caller 等價。完整 ABI、固定配置、installed provider 及硬體狀態仍未證明。

## 使用與證據

```sh
sh experiments/tsl9-nv-read-callback/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
python3 CASE/implementation/provenance.py --project-root ROOT --firmware ORIGINAL_V4160.bin
```

CASE 支援 workspace 的 apk-analysis/tsl9-v4160-callback-frontiers-2026-10-22 與交付樹的 analysis/v4160-callback-frontiers-2026-10-22。NEW 必須是 model/build 下尚不存在的目錄；省略時使用 UUID。正式 W 產物在 build/verified-v1/{c,cpp}，保存 object、完整 IR/disassembly、MD 三項輸入、實際工具與 resource stdint.h hash、原始 logs、source pins 與 receipts。預設 check 只驗來源/metadata；顯式 receipt 才唯讀驗證真實 artifacts，不重新編譯或執行。provenance 或 check --firmware 才重讀原始韌體並做有限靜態解碼。

固定沿用既有 NDK/-Oz/rv32imac_zicsr_zifencei 配方，未加暫存器 bank、未掃 flags、未手工產 opcode。沒有 link、BIN 或刷寫。original-1979a-197b8.bin 只是30B原始來源證據切片，不是重建韌體。Python/sh 原始碼可跨平台；此輪 native 結果限定既有 Windows NDK 工具 hash。Git Bash 先前啟動被拒後未重試，sh runtime 未驗證。新增文字用 LF、單一 EOF newline 及 Git 式空白檢查；原始 compiler logs 保留實際 bytes。

初版 build/native-v1 中 C 的編譯/replay 通過；C++ 也編譯成功，但 probe 拒絕合法的 call noundef i32 返回屬性。只修這項 IR parser 表示差異後，以完全相同 C/C++ source/flags 建立 verified-v1，兩份正式 replay 都通過。初版 raw artifacts 與 initial-probe-snapshot.py 保留作歷史，不冒稱目前 probe 的 replay 證據。
