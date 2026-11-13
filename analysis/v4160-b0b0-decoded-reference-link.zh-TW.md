# B0B0：使用原 BIN 解碼位址的隔離 reference link

本紀錄是離線選定區段診斷，不是正式 provider 或完整 firmware 驗收。原 reference-link 的 18 個外部 witness 原先直接取自 pinned spec 的 `target_PC`；本機新 wrapper 先用已發表的 `experiments/v4160-record-helper-reference-targets/verify.py` 對同一份 pinned BIN 解碼 spec 列出的 51 controls 與 11 AUIPC/ADDI pairs，從解碼結果取出 18 個地址，將原 spec-derived 值僅作一致性檢查。第 19 個 `destination` 另由原始 B0B0 AUIPC/SB 計算，為 `0x2000beeb`。

## 本次實測

- 隔離 wrapper 的合成測試在 Python normal 與 `-O` 各 **16 項通過**，涵蓋清單、碰撞、型別、不一致負例與 decoder 值送入兩模式的接線測試。
- 已固定的本機 Clang 與 LLD 執行 C11、C++17 兩種離線編譯及部分連結；selected facts 比對通過，使用 19 個 ABS witness 的 final linker 各退出 0。各有 68 個選定 sections 與 BIN 比較結果 `TOTAL matched=910 mismatched=0 missing=0`；其中只有 B0B0 的 10 bytes 使用隔離 C 候選替換，其餘 900 bytes 沿用既有、含行內組合語言的來源並重新比對。C11 編譯不代表所有區段均為純 C。final ELF 的 entry 為 0、無 PT_LOAD。
- 原 `run_mode` 的固定輸出仍說 18 個值是 spec 假設；本次 wrapper 實際傳入的是 BIN 解碼後的值，並在執行前提示這個差異。臨時 ELF 等產物清理，未執行、模擬或燒錄 target。

## 範圍與可重播性

18 個地址只由 spec 列舉的 sites 計算；八組連續區段的起始指令邊界仍是未獨立證實的假設。地址相符不證明完整 CFG、未列出的引用、實際 provider code/data、私有 ABI、loader 或 runtime 行為。19 個 `--defsym` 都仍是人工 ABS witness，並非實體 provider；910 bytes 是既選區段，不能當作整個 76800-byte BIN 或純 C 重建。

本機 wrapper `experiments/v4160-b0b0-decoded-reference-link/` 的 `verify.py`、`test_verify.py`、`README.md` 尚未提交；reference／strict／partial／split 重播鏈的多個依賴也尚未提交，**乾淨的 main 無法重播本紀錄**。本紀錄不應被視為 CI 成功。三個本機檔案的 SHA-256 依序為：

- `verify.py`：`43e58a75ed24b59eef371ff675c743d51aeab6e52511e56835ff55c680181479`
- `test_verify.py`：`b34e3336efe4fc912d4ac23db1e0a6ce99f470edb4e005437731ff3762f8e4cb`
- `README.md`：`b9d06a3dc6ab992357b3f7b306022a81e14e7e6e14f976c1c8bd366ebf9ea03b`

工具 EXE hash 不固定編譯器 resource headers（包含 `stdint.h`）、DLL、Python runtime 或其他系統依賴，也不消除 TOCTOU；完整環境及工具供應鏈未受證明。後續需審查並發布完整重播鏈，並以實際 provider 取代 ABS witness，再考慮正式來源整合及整機逐 byte 驗收。
