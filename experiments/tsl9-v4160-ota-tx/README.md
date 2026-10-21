# TSL9 V4.1.60：0x8A56 佇列封包準備與交接

[English](readme.en.md)

這是原始 280 bytes／96 指令函式的部分可讀 C11／C++17 重建。實際編譯器產物也是 280 bytes／96 指令，但尚未符合原始 ABI；本階段只產生 `COMPONENT-ONLY-NOT-FIRMWARE.elf`，不產生 BIN，也未取代現有十二函式完整映像。

`src/tx_native.c` 共用具型別的演算法。原始行為包括 unsigned 長度上限 1039、兩次即時讀取的連線欄位與 ROM `+0x13C` 判定、每個 lane 相距 1062 bytes、逐 byte 向前讀寫與低八位加總，以及經 ROM `+0x50` 的無連結尾端交接。這些證據只顯示準備佇列與交接，不能證明實際 GATT 發送。失敗回傳沿用輸入或不透明判定結果，不新增統一成功碼。

HOST 模式把裝置位址當作數字，所有讀寫交給合成 provider。一般讀寫 callback 可編輯合成記憶體與 frame，但須保留寄存器及 known mask；具名 gate／tail callback 可變更 GP、SP、S 寄存器、caller residues 與記憶體。HOST 按原始順序建立及重新讀取 frame，另測試位址重疊、即時 payload、第二次 gate 的 A2／A3、未知或不返回的效果前綴。這是具名演算法模型，並非 CPU 解譯器，也不證明 native 編譯器實現相同 frame 時序。

gate 返回後的 S0 不會被重新限制為 1039。迴圈以完整 32 位 counter 定址，僅比較其低 16 位與即時 S0；HOST 的額外迭代預算只會停止於 `UNKNOWN`，不新增 native timeout 或清理動作。原始 slot 與 RA 值和清除最低位後的 JALR 目標分開記錄；tail 的回傳值保持不透明。

目前實測 Windows HOST 每個語言通過 4 組、107 案例、15,605 檢查，另有 8 個實際編譯的單一語意變異。每次 HOST 執行都先經固定雜湊的本機格式／架構檢查；RISC-V 目標不可執行。工具支援 PE、ELF 與 thin Mach-O，尚未實測 Linux／macOS；fat／universal Python 目前不支援。

```sh
sh experiments/tsl9-v4160-ota-tx/verify.sh --project-root . --language both
sh experiments/tsl9-v4160-ota-tx/verify_native.sh --tool-dir /path/to/llvm/bin --language both
python -B experiments/tsl9-v4160-ota-tx/verify_host.py --project-root . --replay /path/to/verification.json
```

可用 `PYTHON=/path/to/python` 指定 Python。建置目錄採 create-only；native 重播另可指定 `--firmware`，但 `--replay` 不接受建置輸出、語言或 tool-dir 選項。重播只讀取已存在的產物，不重新編譯或執行。

Native 使用已固定的 LLVM RV32IMAC/Zicsr ILP32 `-Oz` profile，C++ 關閉 exceptions。`-MD` 實際涵蓋三個 native 原始檔與 Clang resource 的 `include/stdint.h`；工具、原始檔及 header 均在建置前後核對。未提供 SRAM 符號的嚴格連結必須失敗；數字 `0x2000B18C` 僅供 PC-relative 位址見證，未提供 SRAM／ROM provider 或硬體配置證明。

已知 native 差異包括：編譯器在長度 guard 之前建立 frame、save 順序不同、成功路徑的 fresh stack restores 晚於 descriptor 寫入和 ROM tail slot 讀取，以及控制流程／指令形式不同。尺寸符合不能消除別名、fault、interrupt 或不透明 callee 對 frame／S／SP 的影響。完整原始 ABI、逐指令 GPR 前綴、完整映像整合、晶片相容性、OTA 與實體裝置驗證均為未通過。

詳細來源、獨立檢查、收據及剩餘限制見 `analysis/v4160-ota-tx-2026-10-22/implementation`（研究工作目錄中為 `apk-analysis/tsl9-v4160-ota-tx-2026-10-22/implementation`）。編譯、日誌與執行檔留在本機 `build/`，不隨原始碼封存發布。
