# 0x105c4：局部原址 link replay

本實驗離線編譯、連結及檢查；不執行產生的 RISC-V 產物。必須保留以下 Git tree 路徑與固定的內容：`src/source-build-manifest.json`、`src/native/receive/feature_state_records.c`、`experiments/v4160-new-leaf-turn/leaf.c`、`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`；SHA-256 在 `replay.py` 中。還需要 Python 3、Windows 和既有 NDK Clang/LLD；設定 `TSL9_NDK_BIN` 為包含這兩個程式的絕對目錄，工具 hash 必須符合 `replay.py`。

```powershell
$env:TSL9_NDK_BIN = Join-Path $env:ANDROID_SDK_ROOT 'ndk\27.1.12297006\toolchains\llvm\prebuilt\windows-x86_64\bin'
python -I -B experiments/v4160-105c4-release-link/replay.py
python -I -B -O experiments/v4160-105c4-release-link/replay.py
python -I -B experiments/v4160-105c4-release-link/test_smoke.py
python -I -B -O experiments/v4160-105c4-release-link/test_smoke.py
```

Replay **始終 exit 1** 並回報 `INCOMPLETE_FAIL_CLOSED`、`passed=false`；`checks_passed=true` 僅表示局部檢查完成。失敗時 `checks_passed=false` 並提供 `error`。輸出的命令及診斷可能包含本機路徑，公開前應去識別。測試是有限 smoke；本機另外執行過更完整的負例，但該測試尚未發布，不能稱為 clean-main 測試。臨時目錄正常結束時自動清理，異常或中斷可能遺留。

Replay 使用 manifest 的完整有序 `queue-consumer-a0-a5` C11／C++17 profile，另加實驗用 symbol rename 和 `-nostdinc`，編譯純 C leaf 並用嚴格未定義符號政策原址連結。兩語言的 object、linked ELF 與 fresh 編譯的原 owner 目標 section 均對比固定 BIN；其 base `0x8000` 是假設，目標窗口 `[0x105c4,0x105d0)` 為 `034535007115133515008280`。真實重編譯／連結的 `==5` 負例必須被拒絕。linked ELF 無 PT_LOAD，不是可載入韌體；原 owner 仍含 inline asm。

Smoke 從 hash 固定的 replay source bytes 直接執行，避免使用舊專案 pyc；測兩種 Python 模式、真實 C11／C++17 編譯連結、負例、輸入污染與 raw ELF 變異，以及缺失符號的實際 linker 非零退出。它並非通用惡意 ELF 驗證器。Python、OS、檔案系統、Clang 的 resource headers 和工具動態依賴未 pin；假設沒有並行替換，hash 不是來源認證。實驗性 symbol rename 不證正式 remap、ABI、caller、addrsig、正式整合或完整 BIN 等價。
