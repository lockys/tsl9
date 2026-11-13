# BF13 的 section-backed 重建見證

## 結果與界線

此前 BD5A／BD64 的純 C 原址比較以人工 ABS `0x2000bf13` 提供地址。本輪使用既有重建 startup 的 `__tsl9v4160_ram[35160]` NOBITS carrier，將 `record_flag_bf13` 定義於 carrier output section 內的 `+0x7f13`。這是**重建地址模型的 section-backed witness**，不證原韌體變數的宣告、生命週期、實體 SRAM、真實資料 owner、caller ABI 或執行期狀態。startup source 本身含 inline asm；只稱 BD5A／BD64 兩個 leaf 為純 C。

本輪 C11／C++17 各從完整 `experiments/tsl9-v4160-startup/src/startup.c` 編譯 ET_REL，再以 `ld.lld -r --no-relax --gc-sections -u __tsl9v4160_ram` 擷取 carrier。離線核對擷取前後的 NOBITS section metadata、符號與 RAM 區段無 relocation，並比較原始 reset 138 bytes 及 14 個 relocation 的指定 target 屬性。原 BIN 的 reset 指令靜態計算 `gp=0x20004000` 和 BSS end `0x2000c958`；在正常訪存且正常完成的條件下，`0x2000bf13` 落在清零區間。這不等於觀察了 target 執行。

兩個純 C leaf 分別獨立編譯；setter 為符合原始 bytes 額外固定 x11–x14，getter 使用不同 profile。最終隔離 ELF 的 `.ram` 為 NOBITS，`record_flag_bf13` 是該 section 的 GLOBAL NOTYPE 符號而非 ABS，carrier 是 GLOBAL OBJECT；只含選定兩個 leaf 和該 RAM allocation，無 PT_LOAD、未解析符號或殘餘 relocation。`0xbd5a` 與 `0xbd64` 原址 bytes 分別為 `97070020a38ca71a8280` 和 `170500200345f51a8280`，逐 byte 等於已 pin 的 V4.1.60 BIN 對應窗口。**最終 link 未啟用 GC**；前述 GC 僅用於抽取 carrier。

此提交的 [`witness.ld`](../experiments/v4160-bf13-section-backed-link/witness.ld) 內容等同本機 probe 產生的正例連結腳本；本機另核對生成字串與此檔的 LF bytes 相同，但 Windows 寫入暫存腳本時可能轉換換行。它不自行編譯、建立 `setter.o`／`getter.o`／`carrier.o`，也不檢查輸入，不能單獨當作驗收工具。腳本中的 symbol assignment 是診斷 view，不是對正式 layout 的修改。

## 本機重播與限制

本機最新 probe 在 Python `-I -B` 與 `-I -B -O` 兩種模式各退出 0，分別驗證 C11、C++17 各 1 正例和 25 個負例。負例包含 RAM base／offset 改變、缺少／重複 carrier、額外實際 object、header 搜尋污染、reset anchor 元資料變異，以及修改實際 ELF bytes 後重解析的 relocation、符號、section、PT_LOAD 等案例。上述是有界負例，不是任意不可信 ELF 的完整驗證。

本次驗證工具 **未包含於此提交**：本機 `experiments/v4160-bf13-section-backed-link/probe.py` SHA-256 `27815d6554b6a2f20cd83fe0c87fd790609e2db77de259002930142b88bb5872`、`elf.py` `25a6280fa39c973318d90e47ffc12bbc8fc8068ab68f8c0bdda999d89b35a981`、`test_cli.py` `fc0d5e094b1818dcb6d8af310c68a73c995066cc6f58bf2cbd71e83c3d06ded5`。receipt 與完整重播鏈仍在本機；receipt 只保存結果和 ELF 雜湊而非可重新解析的 final ELF，這些結論依賴 probe 的檢查。不能宣稱 clean-main 重播或 CI 已通過；probe 的執行期間路徑雜湊不保證等於 Python 已載入的程式，這些雜湊也非供應鏈或無 TOCTOU 的證明。

另一次提交前核對 GitHub `main` 的 `591cb969dc38929f814dc9b3c9ad9aba9ff38dcb` 非截斷 tree：startup source/header/layout、兩個 leaf source 與 BIN 共六個檔案的 blob 均等於本機 bytes；這不證整棵來源樹、所有編譯器相依物或後續 main 狀態。未修改正式來源、manifest 或正式 linker guard，未執行、模擬或燒錄 target。完整純 C source、資料 owner、ABI 與 76,800-byte BIN 驗收均未完成。
