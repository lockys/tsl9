# ECALL 原機區域與向量整合

[English](readme.en.md) · [分析與限制](../../analysis/ecall-restore-2026-10-24/README.md) · [來源](src/ecall_restore.v1.c) · [規格](spec-v1.json) · [整合契約](integration-v1.json)

78B／35i 的 8448–8496 分成 14B 入口與 64B 恢復尾段，保留既有 frame、CSR 遮罩、實體暫存器與 MRET。後方 2 個零 bytes 不屬於程式碼。來源與 `src/native/irq/ecall_restore.c` 相同；本機 C11／C++17 產物逐 byte 相同。

既有收據可唯讀重播。在專案根目錄設定 `LLVM_BIN` 為已安裝且雜湊符合規格的 LLVM bin 目錄：

```sh
python3 experiments/tsl9-ecall-restore/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-ecall-restore/build/trial-v1
python3 experiments/tsl9-ecall-restore/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-ecall-restore/build/component-v1
python3 scripts/check-ecall-restore-publication.py
```

已驗證工具是 Windows 的 Android NDK 27.1.12297006／LLVM18；原生檢查目前依賴該工具的 `.exe` 與固定雜湊，尚未證明可跨系統重播。Windows 可用 `python` 取代 `python3`。缺少本機封存產物時，前兩條指令不會重建或下載它們；公開收據不能代替完整本機產物。新單體試編譯可用 `--trial local-new` 建立不存在的子目錄，不覆寫舊收據。

實際部分連結為 1168B code＋456B data／153 RELA／4 UND；alias 只連到真實入口，沒有假 provider。舊來源與指標資料分開核對，不修改凍結 checker 來接受新版 manifest。未重跑歷史負例矩陣。

此 ET_REL 的 VMA 為 0，並非原位址可執行映像。frame 建立者、特殊 CSR、動態 callback、ROM、實體晶片與 OTA 未證；不輸出或燒錄韌體 BIN。
