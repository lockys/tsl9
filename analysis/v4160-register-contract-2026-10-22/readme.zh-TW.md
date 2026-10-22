# 暫存器保留配方與原始 callback 相依

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

這輪以 C11／C++17 實際編譯一個由原始契約推導的完整暫存器保留集合，並追查原始 `0x1987A→0x188E2` 的唯一巢狀相依。**編譯成功不代表原機 ABI 相容；沒有新 BIN，也沒有替換既有元件。**

| 選定入口 | 原始 bytes | 新 bytes／指令 | 新增自有寫入 | 新 frame |
| --- | ---: | ---: | --- | ---: |
| compare `0x200004BC` | 62 | 60／23 | RA、SP | 16 bytes |
| fill `0x2000039C` | 46 | 68／24 | RA、SP、A2 | 16 bytes |
| copy `0x20000332` | 58 | 64／22 | RA、SP | 16 bytes |

每入口只使用一個有來源依據的 mask，C／C++ 共六份實際 ET_REL。演算法與 volatile IO 沿用上一輪封存來源，僅增加官方 help 支援的 `-ffixed-xN`。先前額外 scratch 寫入消失，但三入口都在 guard MMIO 之前新增 stack／RA 操作；fill 也暫時改寫原本保存的 A2。這個結果排除了此配方直接作為原機 leaf 的方案，不能把正常返回時恢復視為完整 prefix 等價。

六物件各保留十一個真實 global FUNC；compare／fill／copy 配方的完整配置量分別454／492／418 bytes、171／187／155 指令，UND／RELA皆零。這些數字包含各物件十個未選函式，沒有冒稱 linker 已移除。三個選定函式合計192 bytes／69指令，分屬三份物件，並非整合映像。[實作與編譯證據](implementation/README.md)；[獨立原始操作數、IR 與 ABI 審查](abi-review/README.md)。

原始 V4.1.60 的 `0x188E2..0x1892E` 為76 bytes／25列，唯一相依 `0x19160..0x1917E` 為30 bytes／12列。對 callback 傳入的 `0x40012400`，先用遮罩 `0x200` 對 `0x4002100C` 做 OR，然後重新讀取並 AND ~mask；不能宣稱恢復最初整字值。有效 private stack、正常存取及無不利 alias／非同步修改等前提下，這條已封閉鏈保存 SP／RA／S／GP／TP。五個原始位元組操作數反例均拒絕；可選既有 ELF 只驗證兩段原始 bytes，沒有整體來源或 installed 身分證明。[來源、前提與 checker](adc-review/README.md)。

下一個來源缺口為 `0x19896→0x1892E`。整個 callback、config word52 生命期、ROM provider、原硬體、Flash／NV ownership、中斷與 BLE OTA 相容性仍未證明。既有550-byte元件及77,824-byte實驗映像保持不變，後者仍明示 NOT-FLASH-VALIDATED。

值得新增的功能提案：離線相容性報告列出每個 leaf 的原始／重建寫入集合、stack prefix、extent 與尚未封閉相依，避免只看正常回傳值就誤判可替換。這是提案，沒有新增硬體功能，也不以報告取代實體驗證。

`check-parents.py` 預設只核對封存來源及相依 hash；各子目錄預設 metadata 模式同樣不宣稱已讀實際物件。實物須明示 build receipt／firmware。只做靜態分析及編譯，沒有執行 HOST MMIO adapter、RV32／ISA 模擬、硬體、連結或新 BIN。Python 入口已驗證；Git Bash 因 `NtCreateDirectoryObject 0xC0000022` 無法啟動，shell runtime 未驗證，未嘗試繞過。
