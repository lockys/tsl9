# Record dispatcher 12A08
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

重建官方 V4.1.60 的 `[0x12A08,0x12A6E)`：102B／35 指令、9 個私有架構區塊。C 算術搭配明示的 frame、暫存器、存取及控制轉移埠；這些區塊不具獨立普通 C ABI。選用 `src/record_dispatch.v2.c`，副本位於專案 `src/native/receive/record_dispatch.c`。

保留48B frame、status／ID／predicate／tag 分支、SP+20→SP+12→SP+22 的 metadata 寫入順序、未寫的 SP+16..19、fresh [0x4004C] 間接呼叫，以及呼叫後 then-live SP／S0／A2／A3。四個原始4B JAL 的 RA continuation 與 post-RET tagged 分支均保留。不可從符號名稱推定 resident 是 memcpy、周邊是 CAN，或已成功傳送。

一組固定 RV32IMAC_Zicsr／ILP32／Oz 配方分別編譯 C11、C++17；版本1的 JAL 被壓縮而拒絕，版本2只對四個 JAL 埠指定不壓縮。完整歷史見 [source-history.json](source-history.json)。正式 `build/verified-v1/{c,cpp}/verification.json` 各通過212個負例、完整IR/SSA/CFG、MD、五個實際 recipes、ELF 與原始689 retained bits；保留9 pending RELA／4 strong UND。公開收據是可攜原件，raw logs 留在本機。

從專案根目錄使用既有 LLVM：
```sh
python experiments/tsl9-record-dispatch/verify.py --language c --out-dir experiments/tsl9-record-dispatch/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-record-dispatch/verify.py --replay experiments/tsl9-record-dispatch/build/verified-v1/c/verification.json --llvm-bin "$LLVM"
```

輸出只供靜態證明；不執行 RV32、MMIO 或硬體。`--require-firmware-ready` 必須拒絕。原位配置、resident/provider ABI、ROM、IRQ、記憶體與 OTA 相容性仍未證明；不是可燒錄 BIN。
