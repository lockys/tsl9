# Dispatch 與 transport 的實際部分連結

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本實驗只以既有 LLVM `ld.lld -r --no-relax` 連結兩份已正式驗證的實物：526B queue/filter/small-provider dispatch.o，以及 280B transport native.o。C 與 C++ 各保留自己的實際上游證據，不新增編譯、adapter、wrapper、stub、ABS provider、完整執行映像或 BIN。

新 `.transport_dispatch` 保留原 dispatch offset 0..526；13 個 transport 私有區塊接續於 526..806。checker 要求 806 bytes、280 instructions、32 個真實 FUNC（30 個私有架構區塊與兩個小型普通 C 函式）、41 個 pending RELA、五個 strong UND、零 global ABS。保留 cold/post-RET 區塊，不以未使用為由刪除。

原 filter 的 C.JAL 引用在組合 offset 464，現綁定 offset 526 的真實 `tsl9_filter_external_8a56`。這是符號定義綁定：`ld -r` 仍保留全部 41 個機器控制立即數 relocation，沒有證明這些 raw targets 已可執行。五個未解析符號為 `9454`、`9b36`、`12abe`、`12a08`、`14d2e`。

`check.py` 重播兩份實際上游正式證據（其 source/IR/SSA/typed operands/MD/recipes/tools/resources 亦重驗），再用已封存的獨立 ELF32 parser 讀取本次實物。新的 join 判定逐函式與兩份原物件比對全部 bytes、symbol ownership、41 份 relocation 重新索引、配置範圍、280 行 LLVM raw readback，並從官方 V4.1.60 BIN 重讀五段來源，核對所有 non-control bits 與控制 RD/RS/C.JAL link/原始目的地。raw ELF 與 typed operand 負例直接執行這些判定，不靠整個物件 hash 拒絕。

於專案根目錄設定 `LLVM` 為既有 LLVM bin 路徑：

```sh
python experiments/tsl9-transport-dispatch-component/check.py
python experiments/tsl9-transport-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --dispatch-root experiments/tsl9-queue-dispatch-component/build/component-v1 --transport-root experiments/tsl9-transport-frame/build/verified-v1 --build-root experiments/tsl9-transport-dispatch-component/build/NEW
python experiments/tsl9-transport-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-transport-dispatch-component/build/NEW/c/verification.json
```

default 只驗來源封存。`--folder MODE --receipt NEW` 只建立新的實物審查收據，`--replay` 唯讀；`--require-firmware-ready` 必須 exit 1。所有路徑由專案根目錄計算，收據用 `${TSL9_ROOT}`／`${LLVM_BIN}`。Python/POSIX sh 無個人固定路徑；不重試受限 Git Bash，sh runtime 未驗證。

仍未知：五個外部 provider、兩個 admission 間接呼叫的 fresh `[0x4013C]`、resident tail 的 fresh `[0x40050]`，及原 queue/filter 其他 opaque call 的實際身分與 ABI。當前 VMA0 診斷部分連結不保留原 AUIPC 的物理位址意義，也不保證 opaque 呼叫後的 then-live S0 與初始 length guard 相同。沒有普通 C ABI、完整 ROM、IRQ/fault/async、原位配置、硬體或刷寫證明。本輪不執行 target、ISA、MMIO、HOST、網路或硬體，`firmware_ready`／installed-ROM／physical-placement 仍為 false。
