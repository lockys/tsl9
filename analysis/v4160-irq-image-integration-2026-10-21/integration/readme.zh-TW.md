# 實際來源整合的離線 IRQ 映像

C11 與 C++17 各自重新編譯 34 個原始載體單元，以及兩個已固定的可讀 callframe 單元。
只在兩份載體副本移除精確選定的五個組語區段，其餘文字不變；由擁有函式的編譯單元透過
forced include 指定原始區段名稱與真正的全域 FUNC 別名。完整來源映像為 76800 bytes，
SHA-256：`47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`。

檢查器只接受 `0x9A44..0x9A4C`（不含終點）八個位元組的精確差異，對應四個完整的雙位元組
堆疊保存指令重新排序。第一個 SP 調整、主函式 offset10 起的內容、四個 helper 與所有其餘映像
位元組均相同。函式正常返回邊界的證據，不能證明保存順序改變期間的逐步或非同步等價。

可攜式重新建置指令，需要 Python 3.9+ 及支援必要 RV32 參數的本機 LLVM：

```sh
python3 -B analysis/v4160-irq-image-integration-2026-10-21/integration/verify_image.py \
  --project-root . --tool-dir /path/to/llvm/bin --language both
```

分析工作目錄使用 `apk-analysis/tsl9-v4160-` 取代 `analysis/v4160-`。
`verify_image.sh` 轉送相同參數，依序選用 `$PYTHON`、`python3`、`python`。
本輪實際執行的是 Windows 上的 Python；POSIX 啟動器提供原始碼，未透過 WSL 或 Git Bash 執行。
可用 `--clang`、`--linker`、`--objcopy` 指定工具，`--firmware` 指定必須符合雜湊的離線原檔；
`--build-root NEW` 必須使用尚不存在的目錄。流程不下載套件、不連線。

每份建置實際驗證 691 個原始配置、686 個保留區段內容雜湊、53 個區段相對標籤、所有原始
非中繼資料符號角色及恰好五個新增 C FUNC、8270 筆區段外重定位的完整符號角色與有號 addend、
原位置六筆 JAL，以及 helper 零重定位，合計 8276 筆。四個不再需要的私有分支標籤與原始 type44
重定位逐一解除；不接受額外配置、例外中繼資料、隱藏函式、新可寫儲存、ABS 假提供者或連結填補。

中繼資料另有精確限制：SECTION 角色不變，FILE 為原始34加兩份可讀程式；保留的 mapping 角色
只允許編號變動，五個選定區段的 `$d` 改為 `$x`。實際 partial link 會將兩個新增單元各自的
`.riscv.attributes` 標記改為未被引用的 local ABS0，僅允許這兩個非儲存標記及兩個新增 `.comment`
標記，不將它們當作提供者。完整映像逐一符合實際區段與 LOAD 的 VMA／LMA，35160-byte RAM
仍為 NOBITS，不輸出到平面檔案；沒有使用原檔補救缺失區段。

嚴格最終連結確實因唯一缺少的 `__tsl9v4160_rom_entry` 失敗。
另一份腳本只指定數值位址 `0x40000` 產生 `ADDRESS-WITNESS-ONLY.elf`，不提供 ROM 內容或行為；
僅由此見證匯出全新 `NOT-FLASH-VALIDATED-irq-callframe.bin`。

每種語言記錄 44 次 LLVM 呼叫、36 份 `.d`，精確涵蓋71個原始 native 輸入及四個副本／adapter，
並比較建置前後來源、工具與證據雜湊，檢查 LLVM IR 結構，保留15個實際 ELF／重定位／映像負例，
全部成功拒絕。這些都是靜態證據，未執行 RV32 或模擬 ISA。編譯採先前已證明的 `-Oz`、停用
outliner、保留暫存器參數；C++ 加上 `-fno-exceptions`，本輪沒有其他最佳化參數搜尋。

`.d` 採用 `-MMD`，涵蓋專案的非系統來源與標頭，不包含編譯器系統／resource 標頭。
本機 LLVM 執行檔雜湊與實際編譯位元組另行記錄。

不重新編譯的實際產物重驗：

```sh
python3 -B analysis/v4160-irq-image-integration-2026-10-21/integration/verify_image.py \
  --project-root . --replay /path/to/build/c/verification.json
```

`replay(root, receipt)` 重驗實際產物與日誌、命令、依賴閉包、目前工具／來源／證據、ELF、重定位、
映像、IR 與15個負例。`check_image.py --project-root ROOT` 檢查封存報告及兩份逐位元組相同的收據
中繼資料；加上 `--require-local-builds` 才要求兩個歷史本機建置封存都存在並重驗。
發布的中繼資料不冒稱已重驗未附帶的建置封存；獨立覆核另行綁定自己的實際建置。

本輪只完成離線來源儲存整合，多數韌體仍為原始擷取載體。ROM、來源外讀取、callback／資料契約、
任意計算得出的內部入口、晶片與板子身分、中斷時序，以及重排保存之間的觀察仍未解決。
尚未證明實體相容、能開機、OTA 或可安全燒錄。沒有執行目標程式、使用模擬器／硬體或網路。
建置與日誌封存只保留本機，不隨文件發布。
