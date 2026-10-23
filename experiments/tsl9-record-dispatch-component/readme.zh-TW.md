# Record dispatch、predicate 與既有 dispatch 的實際部分連結

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本實驗只將三份正式驗證的真實 C/C++ 物件以既有 LLVM `ld.lld -r --no-relax` 組合：806B transport-dispatch、102B record-dispatch，以及 42B eligibility predicate。沒有新增編譯、alias stub、wrapper、假 ABS provider、執行映像或 BIN。

`.record_dispatch_component` 的預定且由 checker 要求的配置為：既有 dispatch 0..806、record 806..908、predicate 908..950。全部 950 bytes、330 instructions、42 genuine FUNC（39 個私有架構區塊與三個小型普通 C 函式）都保留；不刪除 cold/post-RET 區塊。維持 50 pending RELA、六個 strong UND、零 global ABS。

三項真實定義綁定：原呼叫 offset 282 的 `12a08` 指向 record FUNC offset 806；record 呼叫 offset 814 的 `81aa` 指向既有 status FUNC offset 502（原呼叫 offset 300 也保留）；record 呼叫 offset 832 的 `821e` 指向 predicate FUNC offset 908。局部 predicate 的真實分支由 assembler 解析，不新增假 relocation。`ld -r` 的其他 50 個機器控制立即數仍 pending，符號定義綁定不等於可執行轉移已解析。

六個外部 provider 仍為 `9454`、`9b36`、`12abe`、`14d2e`、`18ca4`、`16b7c`。fresh resident copy `[0x4004C]`、transport admission `[0x4013C]` 與 tail `[0x40050]`，及其他 opaque call 的實際身分與 ABI 仍未知。原 length/status/config guard 不保證 opaque 呼叫後的 then-live state，不能從這個部分連結推定成功傳送或 peripheral 型號。

`check.py` 重播三份實際上游完整正式證據，包括原始 BIN、typed operands、IR/SSA、MD、recipes、tools/resources 與 raw controls。新 join 以已封存的獨立 ELF32 parser 檢查全部函式 bytes、符號歸屬、RELA 重新索引、配置範圍、330 行 LLVM raw readback，以及由官方 V4.1.60 七段來源重讀的 non-control bits、RD/RS/RA-link 與原始目的地。上游來源封存及其完整傳遞輸入與本輪輸入一起記入收據。raw ELF／typed operand 負例直接測判定，不以整個物件 hash 捷徑取代。

從專案根目錄設定 `LLVM` 為既有 LLVM bin 路徑，並將各 ROOT 換成實際正式 build：

```sh
python experiments/tsl9-record-dispatch-component/check.py
python experiments/tsl9-record-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --dispatch-root experiments/tsl9-transport-dispatch-component/build/component-v1 --record-root experiments/tsl9-record-dispatch/build/verified-v1 --predicate-root "$PREDICATE_ROOT" --build-root experiments/tsl9-record-dispatch-component/build/NEW
python experiments/tsl9-record-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-record-dispatch-component/build/NEW/c/verification.json
```

default 只驗來源封存。`--folder MODE --receipt NEW` 建立 create-only 實物收據，`--replay` 唯讀；`--require-firmware-ready` 必須 exit 1。收據使用 `${TSL9_ROOT}`／`${LLVM_BIN}`，Python/POSIX sh 無個人固定路徑。Windows 不重試已知受限 Git Bash，sh runtime 未驗證。

VMA0 是診斷部分連結，不保留原 AUIPC 的物理位址意義；私有區塊不是獨立普通 C ABI。沒有 whole-ROM、fault/IRQ/async、resident provider ABI、原位配置、硬體或刷寫證明。本輪不執行 target、ISA、MMIO、HOST、網路或硬體；`firmware_ready`／installed-ROM／physical-placement 維持 false。
