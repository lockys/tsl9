# Queue consumer 與實際 provider 的部分連結

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本實驗用現有 LLVM `ld.lld -r --no-relax` 組合三份真實 C/C++ 物件：queue consumer 的十個私有架構區塊、filter 的七個私有架構區塊，以及兩個以可讀 C 重建的小型 provider。沒有新增假 provider、ABS 位址符號、包裝函式或 BIN。

`src/providers.c` 只以兩個巨集將官方 V4.1.60 的 GP+167 status 與 conditional clear 定義改為 queue 已使用的外部符號名稱，再 ordinary include 原始 C body。adapter 使用原小型 provider 唯一固定配方：RV32IMAC/Zicsr、ILP32、Oz、禁止 relaxation/outlining/unwind；除 A0/x10 與 A5/x15 外固定 x1..x31。C11 與 C++17 分別編譯，C++ 禁用 exceptions。三項實際 MD 依賴為 adapter、原 C body 與編譯器 stdint.h。

預期且由 checker 實測的 `.dispatch` 為 526 bytes、184 instructions、19 個真實 FUNC；queue/filter/provider 分別佔 offset 0/314/502，status/clear 佔 502..508/508..526。這些名稱與官方 PC 是追蹤身分，診斷 ET_REL 的 VMA 為零，尚未證明原位部署。

`check.py` 自行解析新 ELF，核對全部 FUNC、配置區段、32 份 RELA、原始 BIN 的控制運算元和非控制立即數、完整 LLVM raw readback，並重播凍結 queue/filter 的原始 SSA、typed operand、MD、recipe 與工具資源證據。三個原 UND 符號 `82d2`、`81aa`、`820c` 現在指向真實 C FUNC 定義；`8a56`、`9454`、`9b36`、`12abe`、`12a08`、`14d2e` 仍為六個 strong UND。

`ld -r` 僅完成這三個符號的定義綁定，32 個機器碼控制立即數仍有 pending relocation。checker 分辨 C.JAL 與 C.J，保留 RA link，逐一由官方指令的立即數驗證符號目標；不將尚未套用的 raw target 當成已解析轉移。in-memory raw ELF、typed operand、IR 與 MD 負例必須被拒絕。

在專案根目錄設定 `LLVM` 為既有 LLVM bin 路徑後：

```sh
python experiments/tsl9-queue-dispatch-component/check.py
python experiments/tsl9-queue-dispatch-component/build.py --project-root . --llvm-bin "$LLVM" --queue-root experiments/tsl9-queue-consumer/build/verified-v3 --filter-root experiments/tsl9-queue-filter/build/verified-v1 --build-root experiments/tsl9-queue-dispatch-component/build/NEW
python experiments/tsl9-queue-dispatch-component/check.py --project-root . --llvm-bin "$LLVM" --replay experiments/tsl9-queue-dispatch-component/build/NEW/c/verification.json
```

default 只驗來源封存。actual `--folder MODE --receipt NEW` 以 create-only 方式建立檢查收據，`--replay` 不修改檔案。`--require-firmware-ready` 必須拒絕。Python 與 POSIX sh 不寫死個人路徑；Windows 本輪不啟動已知受限的 Git Bash，因此 sh runtime 未驗證。

第一份 C 的編譯與連結成功，但 reviewer 將 address-significance metadata 誤設為 19 bytes，實際輸入為 10+7+0=17 bytes，因此正式 review 當時停止。`repair-history/` 保留原 checker 與收據 hash；只修正 metadata 推導，C 原產物和 compile receipt 不變、不重編譯或重連結，C++ 仍使用同一配方首次編譯。此機械修正不增加語意通過條件。

已知限制：私有區塊不是獨立普通 C ABI；三個 fresh 間接呼叫、外部 provider 身分與 ABI、AUIPC 原位意義、CSR/IRQ/非同步、有限 poll、resident ROM 與硬體相容性尚未閉合。只做離線 compiler/link/static evidence；沒有執行 target、ISA、MMIO、HOST 行為測試、網路、整機 BIN、OTA 或硬體刷寫。`firmware_ready`、installed-ROM 與 physical placement 永遠為 false。
