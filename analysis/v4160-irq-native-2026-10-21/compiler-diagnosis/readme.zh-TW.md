# 保留 SP 時編譯失敗的實際原因

本範圍只對**凍結且未修改的原版 IRQ-register C/header** 做一個編譯診斷：原 -Oz 組態只移除 `-ffixed-x2`，允許 SP 定址，其餘包含 A1、T0 的保留設定全部相同。這**不是接受的原生候選**，也沒有放寬無堆疊、暫存器、無隱藏呼叫及原配置要求。

C11 與 C++17 產生逐 byte 相同的函式：四個 RCC helper 各 **52 bytes／21 條指令**、初始化函式 **168 bytes／62 條**，另有未預期的本機 `OUTLINED_FUNCTION_0` **16 bytes／7 條**。五個要求的函式都建立 16 bytes frame。已將六個函式完整反組譯逐 byte 綁定 ELF，獨立檢查 raw destination 欄位，確認 SP 與 T0 寫入。沒有未解析符號或可寫 ELF 配置，但已解析的本機 outlined function 仍屬額外實作，無法通過目標的無隱藏呼叫限制。

以下實際 spill 可解釋為何此 backend 對五個原函式都要求 SP；這不代表等效的可讀 C 必然需要堆疊。

| 函式 | Frame 位置 | 實際值與用途 |
|---|---:|---|
| 每個 RCC helper | SP+4 | OR(before, mask)，留給 enabled 分支提交 A0 |
| 每個 RCC helper | SP+8 | select 後的 after，獨立保留至共用 return |
| 每個 RCC helper | SP+12 | 新讀取的 before，由 outlined function 存入，依分支載入 A5 或 A4 |
| 初始化函式 | SP+8 | 常數 `0x02020006`，建立後快取，第三次讀改寫再載入 |
| 初始化函式 | SP+12 | 常數 `0x101D`，建立後快取，第五次讀改寫再載入 |

Helper 的 IR 在共用 volatile store 前先計算 OR、AND_NOT 與 select，再分支至暫存器提交；選取結果的 SSA 另需存活到最後 return。實際機器樣式因此保留上述 before／OR／select。編譯器 `.s` 註解也明列 folded spill／reload。初始化函式的 stack 則是重複常數遮罩快取。原始碼／LLVM IR 沒有 `alloca`，沒有明確 `frame-pointer` 屬性，也沒有實際 frame-pointer 建立指令。尚未重建 allocator 每個內部 pass，但上述 spill 的值與位置已有實際證據。

**本診斷沒有複製、spill 或還原 A1。** Helper 直接兩次判斷輸入 A1，只有 disabled 分支明確寫零，因此「輸入 A1 snapshot」不是觀察到的原因。Main 明確提交 A1=1/0。另外，最佳化器產生 outlined function，四個 helper 透過 **T0** 的 AUIPC/JALR 呼叫，outlined function 也透過 T0 返回，即使 flags 仍有 `-ffixed-x5`。已由 raw RD bits 證實額外 T0 寫入，因此此工具鏈／組態不能只靠 compiler reservation flags 取代最終機器碼檢查。

`analysis.json` 記錄真實位址、SSA 名稱、slot 與編碼暫存器結果。C/C++ 各六個文字控制會拒絕缺失的初始化／helper／outlined 指令列、修改 raw byte、截斷及無法解析的 outlined 列。這些是靜態註記及 checker 控制；沒有執行或模擬 RV32、CSR、記憶體狀態或分支。目標 readiness gate 均保持 false。

本機釘選 Clang 的 hidden help 明確列出 `--enable-machine-outliner=<value>`，其中 `=never` 說明為停用所有 outlining。命令是 `clang -cc1 -mllvm --help-hidden`，exit 0；後續可在明確選定的新來源組態評估 driver 拼法 `-mllvm -enable-machine-outliner=never`，但**本範圍沒有用它編譯**。`clang-help-hidden.json` 只保留相關行及 compiler／完整 help 的 hash；完整 help log 僅留本機。沒有額外測試停用 outliner 的組態或其他來源／flags。

跨平台命令見 [English](readme.en.md)。Fresh CLI 只需凍結來源、本機 tiny parser 與指定 LLVM 工具，不依賴歷史 build，輸出為診斷 ELF，不是韌體 BIN。`results.json` 選定兩份逐 byte 相同的結果副本。唯讀 `check_diagnosis.py --project-root .` 檢查封存資料及目前原始碼；加 `--require-local-builds` 要求歷史本機檔案，並重做完整 bytes 與 spill 註記。只核對 metadata 不等於重新編譯。Object／ELF／IR／組語／log 只保留本機。最初的 gate 因多出第六個函式而拒絕；後續改成明確記錄並拒絕該 outlined 候選，初始輸出仍保留。

下一個來源設計問題是可讀 C 的分支優先計算／store／提交生命期、明確暫存器提交及常數建立；本範圍未測試。未來候選仍須以實際機器碼通過無 SP、無額外 clobber、無隱藏呼叫、正常輸出與原配置限制，才能整合。沒有修改原映像、模型、舊封存資料或交付／發布 checkout；沒有網路、裝置 I/O、目標執行、ISA 模擬或 OTA。
