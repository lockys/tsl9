# 佇列消費與條件分派

[English](readme.en.md) · [來源](src/queue_consumer.v3.c) · [原始逐指令證據](../../analysis/irq-provider-2026-10-23/next-consumer.json)

V4.1.60 的 `[0x12C58,0x12D92)`，包含 RET 後仍可到達的 cold blocks。C11／C++17 的實測候選均為314B／107指令、10個真實 private region；除25筆待解析 relocation 的立即數外，所有位元與官方相同。它們不是10個普通C函式，也不是完整韌體。

C 負責零延伸、常數、fresh間接byte讀取與mask；frame、保留的實體暫存器、SP／CSR及控制轉移由明示架構port保留。resident 呼叫後使用 then-live S0..S7／SP；`12D72` 前沒有重設A1／A2。來源未假設 resident 是memcpy。

`src/queue_consumer.v1.c`／v2保留失敗編譯證據：LLVM對relaxable fragment旁的label型 `.reloc` 報錯。v3以原生 `jal ra,symbol` 及當前位置相對 `.reloc .-2/.-4` 表達真正符號引用，沒有填入provider地址或opcode陣列。

```sh
python3 -B experiments/tsl9-queue-consumer/probe.py --version 3 --out-dir experiments/tsl9-queue-consumer/build/my-new-probe
```

輸出目錄必須不存在；沿用明列的本機LLVM與單一固定配方，不下載工具。`build/probe-v3-lf/measurement.json` 是量測，不能替代正式語意檢查。ET_REL保留八個真實UND provider及25筆relocation，不能直接作為BIN。未執行target／ISA／MMIO，未證明硬體、完整IRQ／resident ABI或OTA相容性。

正式檢查器為 [verify.py](verify.py)，收據在 `build/verified-v3/{c,cpp}/verification.json`；[公開C收據](../../analysis/queue-consumer-2026-10-23/receipts/queue-c.json)／[C++收據](../../analysis/queue-consumer-2026-10-23/receipts/queue-cpp.json) 與原始可攜收據逐byte相同。各295負例（264個raw ELF重新解析、8個typed rows、18個SSA／port、2個完整IR、3個MD）皆拒絕；所有負例停用whole-ELF pin，其中293個也停用完整IR pin。230B是完整非控制指令，2163是包含控制指令operand在內的保留bit數；兩者範圍不同。

```sh
python3 -B experiments/tsl9-queue-consumer/verify.py --replay experiments/tsl9-queue-consumer/build/verified-v3/c/verification.json
```

加上 `--require-firmware-ready` 會拒絕並exit1，因為呼叫尚未解析且原機相容性未證。來源已統一檔尾LF，[src/native/receive/queue_consumer.c](../../src/native/receive/queue_consumer.c)與當前v3逐byte相同。舊來源及v1收據保留本機；本次正式v3與來源整理v4均重新編譯，不冒充原收據。
