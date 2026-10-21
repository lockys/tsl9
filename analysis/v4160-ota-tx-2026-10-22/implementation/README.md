# 0x8A56 TX 部分重建：來源、HOST 與 native 證據

[English](readme.en.md)

本階段實作 `experiments/tsl9-v4160-ota-tx/src` 的共用 C11／C++17 演算法，實際產生 280 bytes／96 指令的 RV32 元件。尺寸符合原始配置，但原始 ABI、完整映像整合與實體相容性皆未通過。既有十二函式映像保持不變；沒有新的 BIN，也沒有執行或模擬 RV32、連接硬體或第三方服務。

`results.json` 選定四份實際 HOST／native 收據；`receipts/` 是逐 byte 相同的中繼資料副本。完整 `.o`、`.ll`、`.elf`、`.d`、測試執行檔及日誌只存在本機排除的 `build/`，不列入發布成員。預設檢查只驗證封存的原始碼與中繼資料，不能宣稱已讀取那些建置產物。

```sh
python -B analysis/v4160-ota-tx-2026-10-22/implementation/check.py --project-root .
sh experiments/tsl9-v4160-ota-tx/verify.sh --project-root . --language both
sh experiments/tsl9-v4160-ota-tx/verify_native.sh --tool-dir /path/to/llvm/bin --language both
python -B analysis/v4160-ota-tx-2026-10-22/implementation/check.py --project-root . --receipt /path/to/fresh/verification.json
```

研究工作目錄的 `analysis/` 對應 `apk-analysis/tsl9-`。`--require-local-builds` 明確重播原始本機四份封存；發布後可用 `--receipt` 指定該環境新建的收據。Native `--firmware` 只做固定 SHA-256 的原始證據比對，會傳入重播；已實測同內容、不同位置的副本。`--replay` 拒絕建置用 output、language 與 tool-dir 參數。

HOST 每個語言通過 4 組、107 案例、15,605 檢查與 8 個實際編譯語意變異；另有獨立 provider oracle 的 4 組、31 案例、78,283 檢查與 14 個編譯變異。內容涵蓋完整 32 位長度、連線選擇、即時 GP／S／SP、frame 重新讀取、第二次 gate 的 A2／A3、byte overlap 回饋、窄寫入、未知／HALT／TRANSFER 前綴、HOST 預算與不透明 tail 回傳。每次 HOST 執行都必須通過不可變更的本機 executable guard；實際 RV32 物件被拒絕於 subprocess 之前，目標啟動次數為零。

Native 每個語言實際執行六個工具指令：Clang resource-dir 查詢、C／C++ 編譯、LLVM IR 產生、靜態反組譯、缺少 SRAM 符號的嚴格連結，以及數字 SRAM 位址見證連結。重播核對完整 argv、順序、來源、flags、退出碼、日誌、產物與 `-MD` 規則：三個 project inputs 加一個實際 Clang `include/stdint.h`。不是沿用舊 header 數量。沒有提供 ROM 實作；`__tsl9v4160_data_2000b18c=0x2000B18C` 是明示 ABS 數字見證，未配置 SRAM。

靜態子集檢查包括唯一 AX 配置、無額外 helper／writable data、完整 280 bytes 反組譯覆蓋、96 條欄位解碼、指令邊界內 CFG、兩次帶 RA 的 gate、尾端 `JR T1`、HI20／LO12_I 的正確配對及實際數字目標、15 個 lexical volatile sites 的寬度、A2／A3 read-write outputs 和真正 `musttail`。Lexical IR 順序不等於分支路徑的完整效果證明。另有 5 個反組譯／IR 負控制、獨立 7 個實際 native operand 變異與 2 個 linked-ELF 變異。

已明確拒絕的 native 條件：原始 guard 在 frame 之前，但 compiler 先存 stack；原始 save 順序不同；成功路徑應在 descriptor 寫入前還原 RA／S1／S2／S3，且在 ROM tail slot 讀取前還原 S0，compiler 卻較晚全部還原。控制分支、sentinel operand、commutative operand 與 GP 尾段形式也不同，不能套用既有僅重排相同 word 的 ABI pass。HOST 以原始 frame 時序模擬 named callback，不會據此把 native 的 frame／fault／alias／interrupt 限制標成通過。

原始證據位於同層 `source-review`，96 指令欄位與 40 個原始 operand 控制已封存。其封存後 JSON tuple/list 公開 wrapper 問題以獨立 `source-review-v2` 修正，未修改舊封存。`code-review` 是獨立 HOST oracle；`ABI-review` 是獨立 native 子集、數字連結與 gap ledger。所有元件均保持離線、合成與靜態的證據界線。
