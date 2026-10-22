# 真實 C 函式與原 caller 的靜態整合

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

這是離線實驗候選，並非已驗證可燒錄的原機韌體。原77824-byte source-wired映像SHA256為 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`，其中原始 `0x19896` 的4-byte JAL尚未修改。新assembler來源只表達對真實C symbol的JAL；由LLVM assembler與lld產生並解析實際 `R_RISCV_JAL`，不是手工opcode或數值ABS provider。

獨立ABI審查只允許明示前提下的19896正常caller投影：有效aligned/private/nonwrapping144-byte stack、正常存取、stack與code/config/MMIO不重疊、沒有非同步干擾，且不把callee的私有frame殘值視為觀察輸出。原callee完整ABI、fault／IRQ／physical等價均未通過。

兩個精確RX LOAD分別為 `0x19896/4B` 與 `0x1B000/110B`，沒有header／hole／NOBITS借位。真C函式定義仍為110B，與輸入native.o中的函式逐byte相同；其餘四個真實global函式由linker GC實際移除。caller JAL的RA仍為 `0x1989A`。

保留的77824B中，只有offset71831、71832、71833三個bytes改變；原88-byte ADC函式仍保留。附加一頁，由110B真C碼與914B明示FF頁尾資料構成。FF是封裝資料分類，raw BIN不編碼硬體execute權限。總長78848B／77個1024B頁，僅滿足既有數值頁範圍，不證明Flash ownership。

C11／C++17生成相同候選SHA256：`ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`。四個實際image操作數反例修改繼承byte、caller、C payload或頁尾，均拒絕。default checker只查metadata；`probe.py --replay FILE`會讀實際ELF／native／BIN／獨立ABI收據並核對來源、工具、每個實際LOAD及整個preimage差異，不重新編譯或執行。

候選繼承舊568-byte OTA元件與其ROM位址witness限制，不能從這次新ADC注入推論整個映像來源、ROM身分、BOOT、中斷、記憶體 ownership或BLE OTA已驗證。新舊候選分開保存；沒有原生、MMIO、ISA或硬體執行。
