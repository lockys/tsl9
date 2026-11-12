# V4.1.60 OTA dispatcher：直接連結障礙

範圍為離線靜態閱讀；未編譯、執行 target、模擬或設定硬體。以下區間均為半開區間；引用的編譯結果是歷史記錄。本回合正常及 Python `-O` 重跑 `tests/test_ota_full_image_contract.py` 各 4 項通過，僅驗證固定檔案離線比較與合成資料檢查。

## 現行鏈路與證據

- `experiments/tsl9-ota-dispatch-inventory/verify.py` 從 `scripts/build-v4160-source-candidate.py` 的 `selected` 與逐片段比較式做 AST 靜態盤點，驗證選取順序、連續覆蓋及 `src/native/tx_candidate/full-image-payload.json` 第一段 carrier 的長度與 SHA-256，4-byte 資料選取式則另行確認；它不編譯、不驗證執行語義。README 中 130 bytes 是歷史狀態，現行選取在 `[0x14056,0x14c8a)` 的 3,124 bytes 全由片段結果串接，無直接選取的 opaque code；獨立的 `[0x1a69c,0x1a6a0)` 仍取 4 bytes 原始資料。`opaque_original_bytes=3128` 是原載體兩段總長，不是目前 opaque code 數。
- `scripts/source-ota-epilogue.py` 分 C/C++ 編譯片段，檢查 ELF section、符號及預期 relocation；例如 `compile_dispatch80` 在 `0x141ac` 以 `--no-relax` 連結，`--defsym` 將 scheduler 指定為數值 `0x9124`。擷取結果與 carrier 對應切片逐 byte 比較。這些絕對值是個別連結的數值見證，不證明 provider 的內容或 ABI。
- `scripts/verify-conditional-full-payload-link.py` 將各片段結果按固定的位址順序串接，整段再與 carrier 比較，轉成 `.byte` section object；**不是將原片段 objects 直接連進最終 ELF**。它在條件 TX RAM 模型和三個資料別名下，測試 strict link 應僅缺 `tsl9_boot_resident_40000`，另測試缺 code/default section；給 ROM 數值後檢查 section backing、別名、連續映像、雜湊及無 `PT_LOAD`。`experiments/tsl9-ota-dispatch-inventory/test-reassembly.py` 檢查此整段 guard 對截斷、重排、變異的拒絕。
- builder 另將選出的位元組包成 C 陣列 object，讀回 section，與其他 source spans 拼成 76,800 bytes，要求 SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`，且與條件診斷映像逐 byte 相等。詳見上述 builder；`experiments/tsl9-ota-dispatch80-source/README.md` 記錄歷史 C/C++ 結果。相等是相對 candidate/carrier 的證據，非獨立原廠 provenance、語義或可刷寫證明。`analysis/ota-full-image-offline-contract.md` 的歷史比較顯示，該 TX integrated candidate 與 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的本機原始參考 BIN 都為 76,800 bytes，但有 93 bytes 不同；OTA carrier 範圍相同。本回合重跑該固定檔案比較；不能把 builder 相等宣稱為原始 BIN 全映像相等。

## 主要障礙

1. 片段不是獨立函式：`src/native/receive/ota_dispatch_14122.inc` 使用既有 `sp`、`s0`、`s1`、`gp`，跳往共用 epilogue；`ota_dispatch_141ac.inc` 記錄 `0x141ae` 跨片段入口並跳出自身。拆開各自呼叫會失去既有 frame、暫存器與控制流契約。裸函式內的原 PC 相對跳轉亦依賴固定布局；逐片段原址相等不等於一次直接連結正確。
2. 個別 object 的 relocation 與局部標籤位移需在共同布局仍指向正確 owner；`--defsym` 可解決數值卻不提供真正 section/實作。條件診斷的三個資料別名雖檢查 section backing，`experiments/tsl9-conditional-data-providers/README.md` 明示全域索引界限及 RAM 所有權未證；resident `0x40000` 的內容與 ABI 也未證。不要把另一 strict 配置的 UND 數量與此配置混算。
3. 來源如 `ota_dispatch_14122.inc`、`ota_dispatch_141ac.inc` 是 `naked` 加 `__asm__ volatile` 的逐指令重建，而非純 C 語義復原；C/C++ 模式成功本身不排除 inline asm 或證明可攜性。

## 建議的 fail-closed 門檻（尚非現有通過結果）

- **共同 frame／CFG**：列出每個入口、跨片段邊、共用 epilogue 和各邊活躍暫存器、SP 偏移及保存/恢復契約；對所有直接邊和可識別間接入口逐一證明落在指令邊界及一致狀態。任何未知入口、未覆蓋邊或 frame 不一致即拒絕；不可用獨立函式呼叫假設補洞。
- **直接物件與 owners**：以實際片段 objects 一次固定原址、無 relaxation 連結；檢查 section 精確覆蓋無縫隙/重疊，逐項比對 object relocation 的位置、型別、符號、addend 與最終解析目標。跨片段及外部 code/data 目標須檢查地址、大小、權限與真實 section owner。局部診斷僅可允許明確列舉的 resident UND，其餘未知 UND、數值佔位、錯誤 owner、越界或未解釋 relocation 一律拒絕，結果仍標示不完整。完整映像門檻則需 resident 實體 provider 與 ABI 證據、無未解契約；數值見證不算完成。
- **純 C 與 inline asm 分級**：若宣稱純 C，對所有納入的預處理來源及其依賴拒絕 asm、naked 與機器碼/`.byte` 代碼替身，並保留可稽核清單；否則明確標為含 asm 的原指令重建。兩種模式均需 C/C++ 各自檢查，不能以編譯通過代替語義證明。
- **固定原址 candidate byte-identical 重現門檻**：直接連結產物的 dispatcher 必須逐 byte 等於 carrier、全映像地址範圍與 76,800 bytes 候選逐 byte 一致且雜湊相符；這不等同原始 BIN 重現。純 C 語義路徑可另行驗證，其不同 bytes 本身不證語義錯誤，但亦不可宣稱已達原始 BIN 的 byte-identical 目標；驗證 section 與符號 backing、映像無洞無重疊，並對錯位、缺 owner、relocation/byte 變異設負向控制。診斷 ELF 無 `PT_LOAD` 只能支持靜態比較；RAM 所有權、全域索引界限、resident 身分/ABI 或硬體未獲獨立證據時，維持 NOT-FLASHABLE，不得由雜湊推論可執行。
