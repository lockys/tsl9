# Reset 記憶體原生編譯證據

凍結的 C／標頭已實際編譯為 RV32 C11 與 C++17，只允許配置器使用 T0／A0／A1／A2。新 leaf 為 **78 位元組、24 條指令**，選用 fragment 為 **80 位元組、24 條指令**；原始記憶體片段 `0x186BA..0x186F8` 為 **62 位元組、17 條指令**。兩個新版本都未通過原範圍大小條件。結構檢查通過不代表原始佈局或韌體相容性通過。

Leaf 是帶有 RET 的新可呼叫介面；原片段直接落入 `LI T0,31` 與 CSR 初始化。舊的複製字 T0 在下一條指令立即被覆寫；本元件不承諾相同 T0 殘值，也未證明入口／IRQ 相容。共用 C 中的最終 A0／A1／A2 承諾另由 hosted 測試驗證。完整原生迴圈語意與逐點暫存器行為仍未證明。

原生 CFG 包含兩個迴圈 SCC：向前交錯的 word 複製與 word 清零；兩者保留無符號判斷。每條實際 ELF 指令的位元組、邊界、目的欄位與內部分支／落下路徑均有檢查。只接受原始 scratch 子集寫入，不接受 SP／GP 寫入、堆疊存取、隱藏 memcpy／memset／函式庫呼叫、可寫配置或冒充原始符號。CFG 刻意保留循環，不推論任意 GP 條件必定終止，也不替 C 程式加入逾時。

LLVM IR 有三個獨立空 asm GP 觀察與記憶體 clobber、一個 volatile READ32 位置及兩個 volatile WRITE32 位置。實際基準機器碼有四次 GP 運算元讀取，因為 Clang 在清零入口判斷後重新計算指標。因此本結果限定一般固定 GP 環境，未證明逐點 GP 快照或非同步 GP 改變行為。經明確授權的單一 clear-step barrier 診斷版本將實體 GP 使用減為三次，但仍為 78 位元組；此版本未採用，主 C／標頭保持不變。

## Fragment 仍缺少接續實作

選用來源寫的是 `c.j __tsl9_reset_resume_186f8`，但此 Clang 組譯器實際產生 **四位元組 JAL x0**，只有一筆 `R_RISCV_JAL` 重定位，類型 17、位移 76。沒有宣稱二位元組壓縮跳躍。物件仍保留唯一未定義的接續符號；沒有提供接續實作時，嚴格連結確實失敗。

獨立的 `ADDRESS-WITNESS-ONLY.elf` 只將符號數值綁定到 `0x186F8`，新 helper 放在診斷位址 `0x1000`，避免重疊，沒有提供接續程式。若把 80 位元組候選放回原始 `0x186BA`，`0x186F8` 會落在候選本身內；原始佈局檢查明確失敗。不會產生造成誤解的原範圍 witness 或韌體 BIN。

四種組態各有三個實際編譯、連結後遭拒絕的控制：寫 A3、寫 SP，以及錯誤的 word 寫入寬度；各另有六個反組譯控制，拒絕遺失首筆／內部／尾端指令、竄改位元組，以及無法解析的內部／尾端行。`receipts/` 發布四份與原收據位元組一致的 JSON；物件、IR、ELF 與日誌只留分析工作區。`results.json` 保存原產物路徑與雜湊供稽核，不表示每份 checkout 都有這些歷史路徑。

## 新建置與唯讀檢查

需要 Python 3.10 以上及本機 LLVM RV32IMAC 工具。在發布的專案內執行跨平台入口：

```sh
python3 analysis/v4160-reset-memory-2026-10-21/compiler-review/verify_native.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both
python3 analysis/v4160-reset-memory-2026-10-21/compiler-review/verify_native.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both --fragment
```

也可分別使用 `--clang`、`--linker`、`--objdump`。分析工作區前綴為 `apk-analysis/tsl9-v4160-reset-memory-2026-10-21/`，發布版本為 `analysis/v4160-reset-memory-2026-10-21/`。新建置只需目前兩個 C／標頭、本地 `elf32.py` 及 LLVM。已驗證工具為 Android NDK 27.1.12297006、Clang 18.0.2，採用 RV32IMAC／ILP32、`-Os`、freestanding／no-relax，並明確保留其餘整數暫存器。不支援的編譯器輸出會明確失敗。

`check_native.py --project-root .` 會檢查封存、目前來源、驗證器／解析器，以及四份歷史收據中繼資料，明確列出缺少的舊建置封存。加上 `--require-local-builds` 才要求並重播這些歷史產物；它們刻意不隨專案發布。只檢查中繼資料不代表重新編譯。新建置會產生自己的 UUID 目錄與真實收據。

沒有執行原始／重建 RV32 或模擬 ISA，也沒有硬體 I/O 或網路操作。原始 reset 落下／IRQ ABI、ROM 服務、記憶體映射、實機、固定佈局與藍牙 OTA 仍未證明。舊有完整原生映像檢查保持不變。
