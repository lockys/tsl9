# 佇列封裝／轉送 filter

[English](readme.en.md) · [C來源](src/queue_filter.v1.c) · [整理副本](../../src/native/receive/queue_filter.c)

重建官方V4.1.60 `[0x82D2,0x838E)` 的188B／69指令，包含RET後的cold path。C負責mask、shift、OR與長度運算；frame、實體S-register／SP、fresh讀取與呼叫使用明示架構port。七個FUNC是相鄰private regions，不是七個普通C ABI入口。

C11／C++17首次固定配方都產生188B／69指令。166B完整非控制指令及1426個保留bit與官方相同；實際ET_REL仍有七筆relocation、一個真實UND `8A56`。`8368` 的2-byte C.JAL會寫RA=`836A`，不能替換成不寫RA的C.J。S4在拒絕過長資料前已更新，所以非零回傳不代表已轉送。

```sh
# Output must be a new directory. Existing pinned local LLVM only.
python3 -B experiments/tsl9-queue-filter/probe.py --version 1 --out-dir experiments/tsl9-queue-filter/build/my-new-probe
python3 -B experiments/tsl9-queue-filter/verify.py --replay experiments/tsl9-queue-filter/build/verified-v1/c/verification.json
```

正式收據在 `build/verified-v1/{c,cpp}/verification.json`；[公開C](../../analysis/queue-filter-2026-10-23/receipts/filter-c.json)／[C++](../../analysis/queue-filter-2026-10-23/receipts/filter-cpp.json)保留原始可攜LF bytes。每語言186負例：152個raw ELF重新解析、9個typed rows、20個SSA／port、2個完整IR、3個MD；全部停用whole-ELF pin，184個也停用完整IR pin。加入 `--require-firmware-ready` 會拒絕並exit1。

診斷link的VMA是0；PC衍生table、原caller與完整opaque-call／IRQ／memory／晶片／OTA相容性仍未證。不能保證處理兩筆record、resident是memcpy或非零代表成功。未下載、執行target／ISA／MMIO或產生韌體BIN。
