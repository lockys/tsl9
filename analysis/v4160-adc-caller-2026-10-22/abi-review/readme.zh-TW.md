# ADC caller 暫存器配置的獨立審查

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本輪只實測一個完整 caller 配置：允許 x10..x16，固定其餘 x5..x31，另檢查 RA/SP/GP/TP。原生 C 模組與共用演算法維持上一輪封存來源；沒有逐次追逐新暫存器，也沒有重跑 HOST 矩陣。

獨立審查重新從實際 ID2966 原檔核對 14 段來源，共 946 B／352 列，包含 callback、限定清零路徑、RCC、reset-like 相依及 ADC cluster。每列原始 operand 重新解碼；證據不依 PSABI。原 19896 返回後，A0/A1 分別先在 1989C/1989A 重設；A5 在 18986 新讀取後才於 1898A 使用；A4 在實際 enabled 分支的 18A9C 先寫後於 18AA0 用；A3 在 18A7A 先寫後於 18A7E 用；A2 在 198B2 先設為1；A6 在實際 channel16 路徑的 189BE 先寫後於 189CC 用。介入來源沒有先讀 A2/A6/A7，也沒有提早讀取舊 A3/A4。原 A7、T0、T2、T3..T6 全程不讀／寫；T1 僅在 8520 寫15、8524 讀取，正常出口仍為15。

實際 C/C++ ET_REL 完整物件相同：公開入口 110 B／42 指令；五個 genuine global FUNC 共 266 B／103 指令，四個未選函式仍保留並審查。完整原始位元欄位與 LLVM 靜態反組譯逐列一致。實際 compiler help 明示全部旗標可供 RISC-V 使用；實際每個函式均沒有寫入固定 bank。工具、資源 header、全部 `-MD` 來源閉包及成功 log 均核對，UND0／RELA0／ABS0。

公開入口每列保持 A0/A1，只寫 RA、SP、A2..A6。它先令 SP 減16，PC2 保存 RA 至新 SP+12，再借 RA 保存第一次 MMIO 讀值；PC104 從相同位置還原 RA、PC106 還原 SP，最後正常 RET。沒有其他公開入口 stack 存取或新呼叫。14 個原始 volatile 效果的位址、寬度、順序、完整 config word 算式、byte 減一遮罩及新鮮 alias 讀取與前輪獨立 SSA 契約相同。

判定僅限 **原始 19896 caller 正常效果／結果／暫存器投影有條件閉合**。既有有效、對齊、不 wrap 的私有144 B stack 區間，包含128 B callback 與最深16 B 子 frame，因此可容納新 frame。新保存字位於 callbackSP-4，與當前 config 的 callbackSP+32..63 分離；還須不與 code、MMIO、其他 live 或外部可觀察資料重疊，存取正常且沒有非同步觀察／修改。未使用私有 frame 的殘值不是這個投影的觀察輸出，不宣稱整個機器 RAM 完全相同。若宣稱整個 callback 正常返回，仍需原 polling loop 在有限次讀取後觀察到非零狀態。完整前提在 `projection.json`，判定由實際 raw 指令與 caller 使用點共同驗證。

原 callee 原先只寫 A3/A4/A5；新版本 RA/SP/A2/A6 的額外及暫時寫入仍不符合完整原 ABI。110 B 比原88 B 多22 B，不能就地替換。fault／非同步／IRQ 前綴、原位置範圍、Flash ownership、實體晶片、BOOT／BLE OTA 與可刷寫性全部未證實。本 scope 沒有 linker、native 執行或 BIN；後續獨立 integration 必須另外提供實際 relocation、位址與來源映像差異證據，且保留上述限制。

每份實物拒絕三個單 operand raw 反例：RA 保存 slot、SP 還原量、最後 store 來源；另拒絕漏 volatile 與錯誤完整 word shift 兩個 IR 反例。`review.py --project-root ROOT --folder BUILD/c --receipt NEW.json` 建立全新審查收據；`--replay NEW.json` 只重新讀實物。省略 folder 可檢查來源契約，明示 `--firmware ORIGINAL` 才讀原檔。`check.py --project-root ROOT` 只驗證封存來源與保留摘要，不冒充實際 build 重讀。

W `apk-analysis/tsl9-*` 與 D/P `analysis/*` 路徑均支援。新文字使用 LF、單一 EOF，default README 與繁體中文完全一致，另有英文。沒有新 HOST、原始／原生／MMIO／RV32／ISA／ESIL 執行、硬體、網路、link 或 BIN。既有 Git Bash 啟動拒絕不再重試，sh runtime 未驗證。
