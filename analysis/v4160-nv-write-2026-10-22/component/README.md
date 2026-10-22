# 八個真實 C 函式的離線元件連結

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本元件用實際 C11／C++17 ET_REL 輸入，透過固定版本 ld.lld 真正連結八個已有 code storage 的 C 函式。未使用 GC 或 relaxation，保留 status／quarter 等未被新 write 入口呼叫的真實函式。沒有外加 ABS provider、stub、原始 opcode carrier 或 ROM 數值見證。

輸入為 394 bytes／148 指令、八個 global FUNC、五筆 R_RISCV_JAL 與五筆 R_RISCV_CALL_PLT。輸出 ET_EXEC 仍為八個函式／394 code bytes；十個呼叫都解析至同一實際 ELF 內的真實函式定義，沒有 UND、剩餘 RELA 或 ABS address provider。STT_FILE 與丟棄 comment 的 local mapping symbol 屬 ELF 中繼資料，不能把它們誤算為虛構地址 provider。

VMA0 僅是元件內部的離線配置，entry 為 write 函式的 offset322；沒有 startup、stack／GP 初始化、BLE、實體 ROM 或可燒錄 image 的意義。唯一 RX LOAD 精確涵蓋394B `.text`；另有一個非 LOAD 的 PT_RISCV_ATTRIBUTES，精確對應非 allocated 的 `.riscv.attributes`，不是可執行配置。首次 reader 誤要求只有一個 PHDR，原始失敗與 source snapshot 留在 build；只修正 metadata 解析，未改指令或連結配方。

C／C++ 的連結後 code bytes 相同，SHA256 `bc6c4438642ee15072836bb30b7e97fdff168b1c49bda5fe9ce9fdde58283aca`。每個未被實際 relocation 涵蓋的 byte 均保持原始 C object 的值；所有函式尺寸、完整 code allocation、entry、segment 與實際 call target 均讀回核對。另一份獨立審查會以獨立 struct reader、每個 immediate bit 與反例核對，不以本 builder replay 代替自己的結論。

**這不是韌體 BIN，也不能燒錄。** 新 write frame／timer 出口暫存器及 helper A1 clobber 尚未符合完整原 ABI；保留的舊 quarter asm-call 宣告另有通用 A1 clobber 缺口，不能從目前固定產物未見反例推論其 C compiler 契約完整。實體 memory ownership、BOOT／ROM、IRQ 及 BLE OTA 均未證實；沒有執行 native／MMIO／CPU／ISA／ESIL 或硬體。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --component-receipt /existing/build/verification.json
```

default 只查 metadata，明示 receipt 才重新讀所有既有 source／tools／ELF／log；不重新連結或產 BIN。實際連結入口為 `probe.py --project-root ROOT --native-folder ACTUAL_NATIVE --tool-dir LLVM --build-root NEW_CASE_BUILD`，只接受新的自有 build 子目錄。
