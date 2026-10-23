# 18CA4 周邊寫入：C/C++ 離線重建
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

選用 `src/peripheral_write.v2.c`，整理副本位於專案 `src/native/receive/peripheral_write.c`。原始範圍 `[0x18CA4,0x18D78)` 共212B／72指令，含RET後三個可達cold blocks。C負責所有算術與volatile讀寫；空暫存器埠和七條明示symbolic edge／RET埠維持原始實體暫存器與配置。七個區塊不是可獨立呼叫的普通C ABI函式。

保留：
- 最多三次分開的fresh statusword讀取，依bit26／27／28短路；未選中回4，尚未讀取record。
- 首次bank+384寫入為原值AND1；ID路徑使用完整input byte8／9，不轉布林或增加ID遮罩。
- input byte10與15做AND並寫回後，才分開兩次fresh bank+388 RMW；不增加DLC<=8檢查。
- payload讀取順序12、11、13、14、16、15、17、18，固定讀八個bytes；最後fresh控制值OR1。
- A2保留第二個payload word的前三個bytes，A4保留最後fresh控制值OR1，A6只在alternate路徑寫入；未選中時A2/A6仍為入口值。

固定一組RV32IMAC_Zicsr／ILP32／Oz配方分別編譯C11/C++17。Native物件有七個真實FUNC、七個local pending RELA、零UND／global ABS；native typed比對只涵蓋非relocated欄位，目的地由真實symbol核對，不能當成raw控制立即數已解析。指定原始位址連結後，全部212B與官方V4.1.60相同，七個控制轉移均已解析，仍不等於實體安裝。

正式 `build/verified-v2/{c,cpp}/verification.json` 各通過197負例：144個native/linked指令變異、10個symbol、2個whole-file tail、21個RELA、14個IR、5個source、1個MD；其中195個不依賴整個ELF hash。完整IR（只移除ModuleID/source_filename）、C操作順序、22個static load／8個store、兩個MD來源、五個實際recipes與13個輸入均核對。不同分支不會同時執行全部22個load；本輪未執行任何target／ISA／MMIO。

[source-history.json](source-history.json) 保留兩版來源與原始輸出：v1被LLVM重排區塊，未選入；v2保留區塊配置。首次正式測試因錯用組語字串定位C產生的IR而失敗；原spec保留於history，修正只改一項負例定位，未改來源或flags。

```sh
python experiments/tsl9-peripheral-write/verify.py --language c --out-dir experiments/tsl9-peripheral-write/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-peripheral-write/verify.py --replay experiments/tsl9-peripheral-write/build/verified-v2/c/verification.json --llvm-bin "$LLVM"
```

`--require-firmware-ready` 必須exit1。信任的Python標準函式庫runtime不是hermetic輸入閉包。周邊型號、caller／resident ABI、alias／非同步效果、完整啟動／ROM／IRQ與BLE OTA相容性仍未知；此輸出不是可燒錄BIN。
