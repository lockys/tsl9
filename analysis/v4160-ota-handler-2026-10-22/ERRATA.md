# 更正：quarter 的靜態呼叫數量

[English below](#english)

前輪 `README.md`、`readme.zh-TW.md`、`readme.en.md` 第 12 行將 native quarter 誤述為四個展開的靜態 callsite。正式 776-byte 物件實際只有 **一個** quarter JAL 重定位，在相對 offset `0x292`；相對 `0x2A4` 的分支返回 `0x28C`，名義四次 quarter 由迴圈執行。原有獨立 ABI 報告與原生物件記錄的是一個 quarter 呼叫點，未發現這些實際產物含有上述四個 callsite。

此為文件錯誤，不改寫已封存來源、seal 或原始測試紀錄。新一輪已重新核對實際 ELF，並保留「停用展開仍為 776 bytes」的否定結果。後續證據與可重跑檢查見[體積縮減與 callee 分析](../v4160-ota-handler-compact-2026-10-22/README.md)。四次寫入仍依賴 callee 保存相關迴圈 state；既有完整 BIN 未因此改變。

## English

Line 12 of the previous three analysis READMEs incorrectly describes four unrolled native quarter callsites. The formal 776-byte object has **one** quarter JAL relocation at relative offset `0x292`; the branch at `0x2A4` returns to `0x28C`. Nominal execution performs four iterations. The sealed independent ABI data and actual object record one quarter callsite.

This corrects prose without rewriting sealed sources, seals or historical test records. The new milestone rechecks actual ELF data and retains the negative result that disabling unrolling still produces 776 bytes. See the [new analysis](../v4160-ota-handler-compact-2026-10-22/readme.en.md). Four writes remain conditional on callee preservation of loop state. The existing complete BIN is unchanged.
