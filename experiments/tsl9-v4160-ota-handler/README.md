# V4.1.60 OTA handler 可讀 C/C++

[English](readme.en.md)

重建 `0x9C4A..0x9E5C` 的 U/S/W/R/E 演算法，共享來源支援 C11/C++17。原始 body 為 530B／169 指令；本輪 native 實測 776B／285 指令、112B frame，尚未符合原始範圍或完整 ABI。未整合、未輸出 BIN、未執行 RISC-V，也未驗證實機 OTA。

W 保留 fresh GP active byte、BE16 page、原始無號範圍條件、寫入前 offset 加 256，以及每個回讀先 Flash word 再 source word。名義目的地是 BOOT alias `0x08001000 + page*1024`，並非 Runtime 自刷。R 沒有附加 W 的頁碼限制。U/S 的 UID 長度為 `(length-1)&255`、原始零回傳表示成功；S 保留呼叫前 stack byte 與呼叫後 live S1 的差別。

`src/ota_handler.h` 定義 named algorithm state、合成 memory effects 與 opaque callee 邊界；不是 CPU interpreter。只有 call provider 可修改 named state。memory provider 可改合成 memory，不能偷偷修改 named state／args。`defined_argument_mask` 只保證選定參數投影；W reply 額外保留 A3 最後 source word、A4=1024、A5 mismatch offset。其他 scratch residues、完整 raw8、物理 SP/RA/S 暫存器 prefix 均未證明。沒有統一成功狀態碼。

HOST 正式每語言 10 cases／8292 checks，另 3 個實際編譯語義反例；獨立審查每語言 16 narratives／18 dispatches／898 checks，另 4 個編譯反例。這些是 synthetic HOST 結果，不能替代 native ABI 或硬體證據。診斷 budget 不會變成 native timeout。

```sh
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root . --language both
sh experiments/tsl9-v4160-ota-handler/verify.sh --project-root . --language both
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root . --replay PATH/verification.json
```

HOST 每次 executable launch 都使用封存 machine guard；replay 重新解析實際 executable。已實測 Windows HOST。介面可攜不代表已在 Linux/macOS 實跑；macOS guard 支援 thin Mach-O Python，不支援 universal/fat Python。

native 正式入口在 `analysis/v4160-ota-handler-2026-10-22/implementation/verify_native.py`，工作樹則位於 `apk-analysis`。明示使用本機 pinned LLVM，產生 ET_REL／IR／完整反組譯／MD，不 link：

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --tool-dir /path/to/llvm/bin --language both
python3 -B apk-analysis/tsl9-v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root . --replay PATH/verification.json
```

native 保留 9 個真 UND、23 RELA，沒有 ABS provider、stub 或 libc 替身。一般 callee 的 S/SP 保存只是條件，HOST 可變 named state 不證明 native 的物理實現。四個 exact recipes、source/tool before-after pins、實際 `-MD` 三個來源與 Clang `stdint.h`、所有產物和完整 raw byte coverage 可唯讀重驗。產物預設在新的 UUID `build/`，拒絕覆寫。原始 BIN 不參與產碼。

正式 metadata、文件與 seal 可發布；`build/`、exe、object、IR、logs 不包含於發布集合。`probe.py` 是舊版 752B 診斷，不是正式 producer。完整目標仍需處理 246B 大小差距、frame／raw register／callee ABI 及實際 provider 整合。
