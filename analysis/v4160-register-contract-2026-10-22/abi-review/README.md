# 固定暫存器配置的獨立 ABI 審查

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

這次三組完整暫存器遮罩均通過編譯，但沒有滿足原始 resident leaf ABI。實際 C/C++ 選定入口分別為 compare 60 B / 23 指令、fill 68 B / 24 指令、copy 64 B / 22 指令；每個遮罩的兩種語言產生相同完整物件。

遮罩由原始每個 leaf 自己寫入的暫存器加 A0/A1/A2 推導，保留其餘 x5–x31；不追逐新暫存器反覆調整旗標。實際 compiler help 明示每個使用旗標支援 RISC-V。機器碼移除了上一輪 compare A6、fill A3/A6/A7、copy T0/A7 的額外寫入，但三個選定入口均新增 16 B stack frame、RA 保存與還原、SP 與 RA 寫入；fill 還暫時改寫 A2。旗標支援與編譯成功無法證明原 ABI 成立。

每個實際 ET_REL 含 11 個真正全域 FUNC，選定入口之外仍有 10 個函式，完整位元組為 454 / 492 / 418 B；全部程式配置、未使用函式、UND0、RELA0、直接 volatile I/O、FENCE.I、三個 u32 參數與 u32 結果均受檢查。沒有隱藏 context/sret 參數。審查由原始位元欄位與完整 LLVM 靜態反組譯逐指令交叉核對，未執行原生函式。

原始 compare 正常結束時 A4 必須為 guard base、A5 為保存的 guard word，A3 為最後讀到的 byte 或未進迴圈時維持輸入；新版本 A3 是結果、A4 是最後 byte 或原輸入。原始 copy 的 A5 為 base、A4 為保存值、A3 為最後目的 byte 位址，新版本 A3 為 base，進入迴圈後 A4/A5 為結尾位址。fill 的正常 A4/A5 現在匹配，但暫時寫入 A2/A4 與 stack spill 仍不同。完整細節在 `semantic-deltas.json`。

compare/fill 原始碼在可能 fault 的 byte 存取之前先更新 A0；新版本在 byte 存取後更新 A0。新的 stack store 也發生在原始 guard READ32 之前。正常返回時還原 RA/SP/A2，不能消除 fault、非同步觀察或記憶體別名差異。正常映射下資料效果與結果的條件式投影，需要新的 stack 有效、私有且不與其他存取重疊。compare 較短 2 B 不代表尾端可借用；fill 超出 22 B、copy 超出 6 B，均不准入原位置。

`review.py --project-root ROOT --folder ACTUAL_LEAF_LANGUAGE_FOLDER --receipt NEW.json` 讀取實際物件並建立全新審查收據；`--replay NEW.json` 重讀實際物件。每個物件執行兩個真正 raw operand 修改控制與一個選定 IR volatile 控制，全部須拒絕。`check.py --project-root ROOT` 只驗證封存來源與已保留摘要，不宣稱重讀實際 build。`selected-kernels.json` 是這次選定入口完整實測 operand/CFG 清單，不是指令執行器。

沒有重新跑未變更 HOST matrix、原始 baseline build、原生 MMIO、RV32/ISA/ESIL 執行、link、BIN、硬體或網路。舊封存與既有映像維持不變；固定遮罩候選未提升為可燒錄韌體。

交付時發現純路徑問題：來源 pin 的 `apk-analysis/tsl9-*` 路徑，在 D/P 副本使用 `analysis/*`。本輪 reviewer 現在沿用 `case()` 規則解析這兩種配置；原生契約、遮罩、operand 清單與通過條件完全不變。原 reviewer、原 seal `9df1696d…` 與舊實際收據保留在 `repair-history/path-resolution-2026-10-22` 記錄及原收據位置。修正後以同六份既有實物建立全新收據並重播，沒有重編譯或新增 profile。
