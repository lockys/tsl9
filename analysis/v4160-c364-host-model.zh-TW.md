# C364 有界 C 事件模型

## 範圍

`experiments/v4160-c364-state-candidate/{candidate.c,candidate.h,test_candidate.c}` 是離線 host C 模型，不是原始 firmware 函式或正式 source owner。依據 [`v4160-bf13-c364-clear-evidence`](../experiments/v4160-bf13-c364-clear-evidence/README.md) 的 BIN 靜態窗口 `[0xc364,0xc3ac)`，以 callback 表達 byte 訪存與兩次條件式呼叫；不實現原 stack、return address、原生呼叫約定、硬體或指令 faults。

模型依序 fresh 讀 `0x2000bf10`、視讀值呼叫 `0xef76(a0=0)`、讀當時 `s0+22`、視讀值呼叫 `0xbd6e(a0=0)`、讀當時 `s0+23`，最後讀值非零時**向固定 `0x2000bf13`** 寫 byte 0。模型的 s0 初值為 `0x2000befc`，並允許兩個 `call` callback 在返回前更動 s0 和記憶體；讀寫 callback 可產生 bus 記憶體副作用，但不直接接收 s0 指標。這是保守的抽象，並非聲稱兩個 callee 實際破壞 s0。原始 store 固定 PC-relative 位址，不能簡化為向 `s0+23` 寫入。位址按 `uint32_t` 模 2³² 計算，所有 callback 需有效；若 callback 不返回，後續事件不發生。bus 自行決定 alias，`volatile` 不提供執行緒同步；模型不涵蓋所有 fault／中斷或機器碼層級行為。

## 本機實測與重播邊界

本機以 Windows x64 MSVC C11 及 Clang 18 host 模式各執行一般及 `NDEBUG`，正常模型事件測試通過；三個刻意錯誤宏（將 store 改寫讀取位址、重定向零值仍 store、重定向非零值跳過 store）均在預期案例失敗。測試涵蓋八種初始旗標、兩次呼叫改值、s0 重定向及重新讀取、直接 alias、callback 不返回；具體事件可由 `test_candidate.c` 重播。未指定 C 最佳化等級，Python `-O` 不代表 C 最佳化。本機另在 Python normal／`-O` 下驗完整 pinned BIN 和相依證據、各跑六項 runner integrity tests；這些測試不能證 target ABI、完整映像或硬體行為。

在 MSVC x64 Developer Command Prompt，於**獨立暫存目錄**可用已提交三檔做正常 host 測試（路徑改成該 checkout 的絕對路徑）：

```bat
cl /nologo /std:c11 /W4 /WX /D_CRT_SECURE_NO_WARNINGS "C:\path\to\candidate.c" "C:\path\to\test_candidate.c" /Fe:c364-host.exe
c364-host.exe
cl /nologo /std:c11 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /DNDEBUG "C:\path\to\candidate.c" "C:\path\to\test_candidate.c" /Fe:c364-host-ndebug.exe
c364-host-ndebug.exe
```

兩個 `C:\path\to\` 必須指向此實驗目錄；預期各輸出 `all host model checks passed`、退出 0。可另加 `/DC364_INTENTIONAL_BUG`、`/DC364_INTENTIONAL_STORE_ON_ZERO` 或 `/DC364_INTENTIONAL_SKIP_REDIRECT_STORE`，**分別重新編譯**，各應在指定事件比較失敗並非零退出；切勿啟用這些宏作為正常候選。host harness 的 `longjmp` 只模擬呼叫不返回，以確認其後事件未發生。

本次完整 host runner、integrity runner 及其 README **未包含在本提交**，因此不能宣稱 clean-main 已重播完整測試。當次本機檔案 SHA-256：`test.py` `4a260df6ea24c474b62e281fd39d8e249b5586cfddaf5cc3fe20bfb29c546d18`；`test_integrity.py` `f7cdfe98ed84b8f47802306362ee9e434f36a85b9385913e995add7482bb417f`。首次本機重播因 MSVC 本地化輸出解碼成 `cp950` 失敗，修正 runner 對子程序輸出使用 UTF-8 replacement 後才完成兩種 Python 模式；編譯退出碼仍獨立檢查。

正式來源、linker 設定及 manifest 均未修改。尚無 C364 RV32 原址 bytes 或真實 data owner 的證據；不得將事件模型視為 firmware 可執行實作或完整逆向完成。
