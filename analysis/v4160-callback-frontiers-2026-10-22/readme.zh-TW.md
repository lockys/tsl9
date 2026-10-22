# NV callback C/C++ 與正常返回邊界

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本輪從原始 ID2966 V4.1.60 來源連到兩份條件式 resident 候選，再重建 NV read callback。原機晶片、installed resident、記憶體 ownership、IRQ 與 BLE OTA 相容性仍未證明；沒有新的韌體 BIN，也沒有執行原生／MMIO／CPU／ISA／ESIL 或硬體。

## 實際 C/C++ 與獨立核對

原 `0x1979A..0x197B8` 為 30 bytes／13 指令。可讀 C11／C++17 都實際編譯成 32 bytes／14 指令、一個真實 global FUNC，UND／RELA／ABS 為零。兩語言函式 bytes 相同，SHA256 `be3e03eacb688e38d8dbebdd509b900520385a2a2084136c4bdbfdd5f5caad3c`。每次新讀 slot `0x4004C`，實際間接呼叫參數為 `(entry A2, entry A0, uint32(entry A1<<2))`，忽略 callee 回值，正常返回零。這是條件式 register-call 介面，並非恢復出的原始 C prototype。

獨立 reviewer 直讀 ELF、全部原始 operand、LLVM 文字、完整 IR def-use、成功 log 與 `-MD` 閉包，不呼叫 producer replay 作為自己的判定。每語言拒絕五個 raw operand 與三個 IR 反例。原生碼仍多寫 A3，且 slot read／frame 建立、RA 還原／A0 歸零的時序與原碼不同；完整 ABI、fault／IRQ、原範圍就地取代及 resident caller 全部替換均未通過。[C/C++ 來源與實際編譯](implementation/README.md)；[獨立原生審查](native-review/README.md)。

## ADC 私有暫存字在正常出口會重新一致

新的來源證明核對三段 470 bytes／167 列，另重讀先前完整 946 bytes／352 列閉包；前者是後者的子集，不能相加當作新 coverage。原 `0x198E6` 的呼叫支配正常 callback 出口；`0x188E8` 保存 RA，把 callbackSP−4 寫成 `0x198EA`，之後沒有 caller stack store。故在既有正常存取、有效私有 stack／分離／無干擾與 callback 最終返回的前提下，原版與 ADC 候選在正常出口的這一個 word 相同。

這不是 ADC callee 剛返回時、所有 RAM、fault 或 IRQ 等價證明。原 poll 仍可永遠讀到零，無法保證一定返回；六個 raw 反例含可繞過最後覆寫但保留 epilogue 的 CFG 反例。[正常出口支配與前提](frame-review/README.md)。

## config callback 與數值 NV 範圍

原 App 的 record+56 為 `0x1979A`，+60 為 `0x197BE`，+8 的數值為 `0x08077C00`。resident 第一個 read callback 的條件式參數為來源該 NV base、word 數 1、目的 tableSP+12，僅複製四個 bytes。若 fresh slot 確實對應已審查的 candidate copy，且這些值／stack／記憶體保持相關前提，copy 的非零四 byte 路徑在首次使用 A3 前先覆寫它；這個特定呼叫可消除新增 A3 的差異。泛型 null／zero／左移回繞為零的路徑仍可能保留 A3 差異。

write callback 是 50-byte 函式，依序呼叫 unlock、erase、program、lock 與 `0x19764` 的 SysTick-like 輪詢。它固定執行一個 256-byte quarter，entry A1 並不控制寫入長度；正常回傳零不等於控制器成功。table 的條件式配置對應三段 256-byte 數值範圍 `0x08077C00..0x08077F00`（右界不含），仍取決於原 record、預設值、fresh 配置、heap／stack／config 不重疊及未知 callback。這些地址不是 Flash ownership 證明。config+52 與後續 fresh live S0+60 的生命期／間接效果仍需保持條件。[App 綁定、完整 callee 與前緣](binding-review/README.md)。

值得新增的功能提案：離線 NV 相容性診斷，列出實際 read/write 長度、對齊／範圍、callback 前提與所有未證硬體條件，避免把回傳零或數值位址當成刷寫成功。這是提案，未新增原硬體功能。

既有 78,848-byte `NOT-FLASH-VALIDATED-adc-caller-bank.bin` 與全部舊封存保持不變；新 read callback 尚未整合入該映像。預設各 checker 只查 metadata，實物模式須明示 firmware／candidate refs 或 native folder／receipt。Python 入口已實測；既有 Git Bash 拒絕沒有重試，shell runtime 尚未驗證。
