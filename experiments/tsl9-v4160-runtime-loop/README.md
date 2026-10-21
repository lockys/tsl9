# V4.1.60 initialization, main loop and event dispatch / 初始化、主迴圈與事件派送

This C11/C++17 host model reconstructs four selected bodies in ID2966 V4.1.60 (SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`): main `9008..901A`, initialization `9250..9290`, loop `8180..81AA`, and dispatcher `901A..907A`. Ends are exclusive: 220 bytes and 80 instructions in total. Source proof replays the original bytes and rejects 45 raw operand mutations. The model is fixed dataflow written in C, not an ISA interpreter. It executes only our host program over synthetic fixtures.

本 C11／C++17 主機模型重建 ID2966 V4.1.60 的四段函式：main、初始化、主迴圈及事件派送。上述位址終點不含在範圍內，共 220 bytes／80 條指令；來源證據可用原始 bytes 重播，並拒絕 45 個原始運算元突變。這是以 C 撰寫的固定資料流模型，僅執行自寫主機程式及合成資料。

## Observable behavior / 可觀察行為

- Initialization preserves source order for 14 callees, fresh saved-RA loading, and the tail transfer to `17BF6`. Providers see live register snapshots; neither a guessed C prototype nor a success-status check is invented.
- Loop `8180` freshly reads the numeric callback slot through live S2, calls that target, `17002` and `12C58`, then stores live S0 through live S1. Its source has a permanent backedge and no return/restore. A host observation budget leaves the frame in place and never enters the `9012` suffix automatically.
- Dispatcher scans only bits 0..14, reads callback, mode, then argument in source order, and clears one-shot fields before a callback. After a callback, the result uses live S0/S1, discards callback A0, truncates to 16 bits, and freshly restores RA/S0/S1 through live SP. An earlier unknown event bit prevents choosing a later bit.
- The optional resident bridge accepts only the exact selected candidate's explicit MRET transfer with fully known target `9008`. It transfers only represented register knowledge. Strict captured resident data still stops before MRET; a synthetic fixture that supplies an unknown word is a separate conditional experiment.

- 初始化依序保留 14 次呼叫、從當下堆疊重讀 RA，以及尾端轉移至 `17BF6`。提供者接收當下暫存器快照；未臆測原始 C 函式原型或成功狀態檢查。
- `8180` 透過當下 S2 重讀 callback 槽，依序呼叫該目標、`17002`、`12C58`，再透過當下 S1 儲存 S0。來源永久回跳，沒有返回或還原。主機觀察次數用盡時保留堆疊，不會自動執行 `9012` 後段。
- 派送只掃描 bit0..14，依原碼順序讀 callback、mode、argument；單次欄位在呼叫前清除。回呼後以當下 S0／S1 計算低 16 位結果，忽略回呼 A0，再透過當下 SP 重讀 RA／S0／S1。較前面的未知事件位元會阻止選取後方位元。
- resident 橋接只接受指定候選模型已明示的 MRET 轉移，且目標必須完整已知為 `9008`；僅傳遞已表示的暫存器知識。嚴格使用擷取資料時仍在 MRET 前停止；以合成未知字補充的實驗另外標示條件。

## Provider and observation contract / 提供者與觀察邊界

Addresses remain numeric. Memory/RET providers preserve registers; whole-callee providers may alter represented registers and shared memory but must preserve model control/budget. `RETURNED` alone does not establish a continuation: every callee supplies an explicit `returned_to`. Wrong routes transfer; unknown routes stop. Calls are observed after the source's local link-RA assignment, including when a target, provider or observation allowance is unavailable. Tail calls form no new link. Effects that stop do not trigger cleanup, stack restoration or further calls. Unknown bits remain unknown; no RAM, missing firmware bytes or return values are silently zero-filled. Reuse `ml_new_activation` only for a distinct host activation, never as native-PC resumption.

位址始終是數值。記憶體／RET 提供者保留暫存器；整段 callee 提供者可更動已表示的暫存器與共用記憶體，但須保留模型控制及次數限制。單有 `RETURNED` 不代表可以繼續：每次呼叫必須明示 `returned_to`；錯誤路徑轉移，未知路徑停止。觀察呼叫邊界時，原碼的 link-RA 賦值已形成，即使目標、提供者或觀察額度不足；tail call 不建立新 link。停止不會自動清理、還原堆疊或繼續呼叫。未知位元保持未知，不會默默補零。`ml_new_activation` 只建立另一個主機觀察，不代表恢復原機 PC。

## Verification / 驗證

Run `./verify.ps1` and `./verify.ps1 -Cpp` with PowerShell and the configured MSVC BuildTools. The verifier checks the exact firmware, sealed portable source proof, shared type-header dependency, all seven model files, executable and compiler hashes. Run `tests/run-tests.ps1` for the synthetic suite alone. Proof may be supplied with `-ProofRoot`; original firmware with `-Firmware`.

以 PowerShell 及已設定的 MSVC BuildTools 執行 `./verify.ps1` 與 `./verify.ps1 -Cpp`。驗證會核對原始韌體、已封存可攜來源證據、共用型別標頭、七個模型檔案、實際執行檔與編譯器雜湊。只執行合成測試可使用 `tests/run-tests.ps1`；證據位置可用 `-ProofRoot` 指定，韌體可用 `-Firmware` 指定。

## Remaining limits / 尚未確認

Deep initialization callees, ROM scheduler behavior, callback ABI and all physical effects remain explicit provider boundaries. Numeric symbol storage in the native image does not prove these implementations. No original RISC-V bytes are executed or emulated; no BLE, UART, CAN or physical flash access occurs. This milestone produces no new flashable BIN and proves no exact MCU/PCB, installed ROM, interrupt ABI or OTA compatibility. The previous source-identical offline image remains **NOT-FLASH-VALIDATED**.

深層初始化 callee、ROM 排程器行為、callback ABI 及實體效果仍為明示的提供者邊界。native image 中存在數值符號儲存，不等於上述實作已獲證明。本輪不執行或模擬原始 RISC-V bytes，也不存取 BLE、UART、CAN 或實體 Flash；未產生可刷寫的新 BIN，未證明確切 MCU／PCB、原機 ROM、中斷 ABI 或 OTA 相容性。原有來源一致的離線映像仍為 **NOT-FLASH-VALIDATED**。
