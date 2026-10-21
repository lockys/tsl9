# 十一個可讀函式的完整離線映像

[English](readme.en.md)

本輪將既有五個 IRQ／RCC 與六個 Flash 函式的可讀 C11／C++17 來源整合回完整原始配置。兩種語言均已實際重新編譯 42 個單元，產生相同的 76,800-byte 候選映像。**這仍是未經原機驗證的離線 BIN，尚不能宣稱可由藍牙安全刷寫。**

## 實際重建範圍

42 個編譯單元由 34 個原始指令／資料載體、兩個 IRQ／RCC 單元及六個 Flash 單元組成。四個載體只移除原本十一個函式的區段，其餘來源保留。十一個可讀函式共 526 bytes；其餘程式與資料仍主要來自原始載體，不能宣稱已完整還原原始碼。

| 函式 | 原址 | 配置 bytes | 與官方映像不同的 bytes |
| --- | --- | --- | --- |
| IRQ 初始化 | 0x9A42 | 144 | 8 |
| 四個 RCC helper | 0x19124／0x19142／0x19160／0x1917E | 120 | 0 |
| Flash quarter wrapper | 0x9C0A | 64 | 6 |
| Flash status | 0x18E90 | 8 | 0 |
| Flash unlock | 0x18E98 | 30 | 12 |
| Flash lock | 0x18EB6 | 14 | 0 |
| Flash erase | 0x18EC4 | 46 | 21 |
| Flash 64-word program | 0x18EF2 | 100 | 23 |

完整映像 SHA-256：`de159bb345b27250a683e197dd84b04e51a7a7ed89315347395baaea53f68be1`。與官方映像相差 70 bytes，其中八個來自前輪 IRQ 保存順序，62 個來自此次 Flash 元件；前輪候選與官方檔案均保留。

## 證據與檢查

完整配置仍為 691 段；680 段範圍外原始儲存及 53 個 section-relative 綁定保留。新物件實際有 8,270 筆 RELA：8,259 筆範圍外記錄保持完整角色與次數，十一筆來自可讀函式的 JAL。相較原始 8,280 筆，四筆 IRQ helper 與六筆 Flash 內部分支由實際 bytes、PC、條件與目標核對後解除，未偽造舊 private label 或數字 ABS provider。

二十筆外部入口引用分別核對，包括兩個壓縮 C.JAL 的 `PC+2` 返回位址，以及不寫入新 RA 的 tail jump。未連結物件中的原始儲存與完成重定位後的映像分開比較，不能混用兩層雜湊。

嚴格連結仍明確拒絕缺失的 ROM provider。成功連結只採用 `0x40000` 數字位址見證，不提供 ROM bytes。匯出的所有 bytes 須由實際區段與 LOAD 支持；無補洞、NOP padding、原始 BIN 回填、RAM NOBITS 或 ROM bytes 匯出。

每種語言核對 56 個實際編譯／連結／匯出指令、42 個逐一對應來源與 adapter 的依賴規則，以及 194 個實際產物雜湊。二十三個 ELF／重定位／映像反例及三個實際依賴檔反例分別被拒絕；獨立 ABI 審查另有每語言二十個實際產物破壞控制。這些都是離線檢查器證據，不能取代原機測試。

- [實作與實際建置證據](implementation/README.md)
- [獨立來源／配置／映像審查](source-review/README.md)
- [獨立 ABI 與分支審查](ABI-review/README.md)
- [有限的 literal interior 引用搜尋](numeric-interior/README.md)

literal 搜尋在三個精確映像中逐 byte 位置檢查 1,030 個內部位址數值，均無命中；十個合成控制驗證搜尋器。這不是 ROM、計算而來或拆開編碼引用的不存在證明。

## 可攜式入口與限制

在專案根目錄執行 `python experiments/tsl9-v4160-flash-image-integration/verify.py --tool-dir <LLVM-bin> --language both`；同目錄提供 `verify.sh`。只執行主機 LLVM 編譯／連結工具，將 RV32 物件與映像當資料檢查。Windows Python／LLVM 結果不代表 shell、Linux、macOS 或 CI 已實際執行。

Flash program 的原始 `+8` 指令邊界仍未保留；scratch 暫存器、fault／非返回 GPR prefix、IRQ 逐指令保存狀態與非同步等價仍未證明。原機晶片／板子、ROM、Flash、實際 BOOT 版本及 BLE OTA 相容性也未通過。WCH CH32V20x／208 仍是候選，不能用這份成功編譯的映像反證硬體型號。

值得新增的功能是本機更新檔前置檢查與可攜式離線證據匯出：在任何硬體操作前，核對檔案來源、雜湊、角色與版本證據並輸出可重播報告。這些是後續提案，尚未加入原機功能。
