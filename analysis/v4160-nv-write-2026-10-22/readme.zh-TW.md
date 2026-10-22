# NV 寫入回呼、計時器與真實 C/C++ 元件

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

原始 V4.1.60 / ID2966 的 `0x197BE` 寫入回呼及 `0x19764` 計時器已重建為真實 C11／C++17，並共用六個已有的真實 Flash C 函式。完整物件保留八個 global FUNC，394 bytes／148 指令，UND0、RELA10。寫入入口72B／26指令／16B frame，計時器60B／23指令／無frame；兩語言 code bytes 相同。

寫入依序呼叫 unlock、erase、program、lock、delay(1)，返回零；來源是入口 A2，入口 A1 未使用。計時器從 fresh GP+382 byte 計算低32位乘積，對 `0xE000F000` 區塊執行至少12個有序 volatile 效果，無 timeout 地等 STATUS bit0 設定。實體時間單位尚未證明。

獨立來源審查核對294B／115列／六組原始函式，拒絕七個 raw 反例。另一份44B／12列校準關聯審查拒絕七個反例：只有在相同 GP 且無中途寫入等前提下，`GP+382 = (READ32(GP+108)/8000000)&255` 與計時器相連。這44B含已計入計時器來源的4B，不可累加為額外獨立涵蓋率。

獨立 native 審查逐欄核對完整 ELF/raw operands、LLVM 靜態輸出及 C IR，每語言拒絕12個反例。實際 ld.lld 把全部八個 C 函式連成離線 ET_EXEC；十個呼叫全部解析至真實定義，沒有剩餘 UND／RELA／ABS provider。唯一 RX LOAD 精確涵蓋394B code，另有非 LOAD 的 RISC-V attributes metadata。獨立元件審查核對260個可重定位 immediate bits、實際24個變動 bytes，拒絕七個真實 ELF 反例。連結後 code SHA256：`bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`。

**沒有新韌體 BIN，元件不能燒錄。** VMA0只是非實體離線布局。新 write 的 frame／來源保存方式、timer 出口暫存器、unlock／erase 的額外 A1 寫入都與原始不同；保留的未選 quarter asm-call 宣告漏列這兩個 A1 clobber，固定物件未見讀前覆寫反例不等於 compiler 契約完整。完整 ABI、fault／IRQ、startup／GP／stack、實體 ROM／Flash／NV ownership 與 BLE OTA 均未證實。沒有 native／CPU／ISA／ESIL／硬體執行，也未重跑未變更 HOST 矩陣。既有實驗映像保留。

## 證據與實作

- [共享 C/C++ 程式](../../experiments/tsl9-nv-write-callback/README.md)
- [實際編譯與來源封存](implementation/README.md)
- [原始寫入與計時器來源](source-review/README.md)
- [獨立 native 審查與 ABI 缺口](native-review/README.md)
- [校準關聯及適用前提](calibration-review/README.md)
- [實際離線元件連結](component/README.md)
- [獨立 ELF／call target 審查](component-review/README.md)

功能提案：離線診斷校準 byte 為零、截斷／回繞及 GP 設定生命期，區分算術診斷與實體時間；尚未整合為硬體功能。下一步需在新的自有 profile 修正 clobber 契約並研究原 caller 的可觀察暫存器，保留舊封存。
