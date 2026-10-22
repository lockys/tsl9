# ADC caller 條件式相容與新的實驗 BIN

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

這輪保留共享C演算法與真實volatile IO，僅採用由原caller來源推導的唯一完整暫存器bank（x10..x16，其餘x5..x31固定）。C11／C++17實際編譯結果相同：選定函式110B／42指令，完整五函式物件266B／103指令、UND／RELA／ABS為零。A7與T／S／GP／TP均未改寫；新16-byte frame會保存／還原RA，A2／A6仍改寫。

獨立重讀原始946B／352列，確認19896之後A0..A6在使用前被覆寫、A7及其他須保存的暫存器不能逃逸。**僅在有效aligned/private/nonwrapping144-byte stack、正常存取、stack/code/config/MMIO分離、無非同步干擾，且不觀察callee私有frame殘值等前提下，此caller正常效果／結果／暫存器投影成立。** 原callee完整ABI、fault／IRQ前綴及原88-byte範圍均未通過。[編譯來源](implementation/README.md)；[獨立來源與ABI](abi-review/README.md)。

在上述軟體條件下，新增獨立的 [NOT-FLASH-VALIDATED候選](../../artifacts/offline-images/ID2966-V4.1.60-adc-caller-bank/README.md)：78848 bytes，SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`。LLVM assembler/lld把19896的真JAL連到1B000的真C定義，RA仍為1989A。舊77824B前像只有三個bytes改變，原88B ADC函式仍在；附加一頁110B C碼及914B明示FF封裝資料，未借用舊tail或填補未知孔洞。四個未選真實global函式由linker GC實際移除，linked ELF只有兩個精確LOAD。

C／C++新候選逐byte相同。獨立審查直讀ELF、raw JAL與BIN，核對整個preimage、真實C函式、LOAD及GC；不是只接受builder自己的replay。[整合與實檔核對](integration/README.md)；[獨立整合審查](integration-review/README.md)。raw BIN沒有硬體execute權限資訊，77頁只滿足既有數值範圍，不能當作Flash ownership證明。

另讀兩份候選resident的callback後主函式與必要direct依賴：每份8個body、1056B／359列，合計2112B／718列，保留sparse HEX來源，不補洞。主函式會建立heap／table及函式指標；allocator失敗通知由slot400A4對應config+52取得。另有config+56及fresh liveS0+60的computed callbacks，後者只有前callback保存S0時才仍等於config+60。這些callback及heap alias／迴圈仍有未解效果，不能把有界source CFG封閉擴張成整個初始化返回或config52生命期證明。[來源前緣與前提](continuation-review/README.md)。

值得新增的功能提案：離線相容性報告列出caller可觀察暫存器、stack範圍、配置callback／NV成對條件及heap分配診斷，協助區分未解前緣與已核對範圍。這是提案，沒有新原機功能。

**此檔不是經驗證可刷寫的韌體。** 它仍繼承舊568-byte OTA元件與ROM位址witness限制；原晶片、installed ROM、BOOT、Flash／NV／RAM ownership、fault／中斷及實體BLE OTA均未完整證明。舊映像與所有舊封存保持不變。全程沒有HOST舊矩陣重跑、原生／MMIO／CPU／ISA／硬體執行或刷寫；只做靜態分析、編譯、link與候選封裝。

預設checker只驗metadata，actual receipts／candidate refs須明示。Python入口已驗證；先前Git Bash的 `NtCreateDirectoryObject0xC0000022` 拒絕未重試，shell runtime仍未驗證。
