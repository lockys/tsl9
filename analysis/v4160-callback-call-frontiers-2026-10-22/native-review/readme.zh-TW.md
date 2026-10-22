# Callback 原生呼叫邊界

[English](readme.en.md)

本獨立審查唯讀檢查既有 624 位元組 C/C++ callback 元件。十五個站點依實際指標載入來源、具辨識力的參數定義、前驅呼叫類別及獨立 LLVM SSA 對照；不以位址排序配對。原生 223 條指令的全部欄位另與 LLVM 反組譯相等；原始證據為 632 位元組、217 條指令。

`selected.json` 記錄已量測的 C/C++ 結果與雜湊，不封存編譯產物。僅通過中繼資料檢查，不代表實際讀過原生產物。本套件不改程式、不重新編譯或重跑 HOST 測試、不執行／模擬目標 CPU，也不產生新 BIN。

## 發現

- 原始 `8800 LHU A5` 與原生 `120A LH A0`，都只把低 16 位寫入 `SH`，之後暫存器即被明確覆寫。符號擴展差異在對應的 `descriptor_send`（`8812`／元件 `1220`）已失效。這關閉該項呼叫邊界差異，並不證明中斷、故障前綴一致。
- 該呼叫的實體 A3/A4，在兩份指令流都沿用對應前一個 gate 的未知輸出；LLVM SSA 亦獨立確認相同兩項轉送。此處未發現漏設 A4。
- 實體 S 暫存器用途不同。例如原始接收呼叫的 S2 為 `40000`，原生保留入口 S2；原始 pending gate 的 S7 名義上為 `40000`，原生 S7 為佇列中的無號半字，該處原生 S4 是遮罩暫存值。這些是已確認的觀測及未知 resident 若觀察隱含輸入時的條件式義務，不直接等於已知 resident ABI 下的功能失敗。
- 名義目標槽位辨識，僅在辨識階段明示採用一般 callee-saved 保留條件。每個呼叫的 A0..A7、S 暫存器、GP、SP 定義，另以 `opaque-all` 全部未知覆寫政策保留。原始透過 live S 暫存器取目標，與原生使用常數基底的差異不被隱藏。
- 配對後的返回偏移不同。僅字面 RA 不同不足以證明不相容，本審查未證明安裝中 ROM 的 RA 契約；候選 resident 本體證據另案處理。

三項聚焦反例分別拒絕實際 D4 指標載入運算元變動、descriptor-send 前的實際 A3 覆寫、SSA 的 A4 替換；另把已儲存指令列反向排列，十五個站點身份仍相同。這些都是靜態檢查，未執行指令或對韌體動態模糊測試。

## 執行

僅驗封存來源與中繼資料，不需要產物封存檔：

```sh
python3 -B native-review/check.py --project-root ROOT
```

實際唯讀檢查元件；新報告須放在既有元件目錄外：

```sh
python3 -B native-review/review.py --project-root ROOT --folder ROOT/experiments/tsl9-v4160-callback-registers/build/RUN/ordered/c --receipt ROOT/analysis/v4160-callback-call-frontiers-2026-10-22/build/native-c.json
python3 -B native-review/review.py --project-root ROOT --replay RECEIPT.json
```

IR 預設讀取同層 `RUN/pre/c/callback.ll`；可用 `--ir-folder PRE_MODE` 明確指定。加 `--firmware FW` 才會另讀並驗證已固定的官方原始位元組，重播時須維持同一模式；未指定時只驗原始指令證據，`original_firmware_read` 為 false。`review.sh`／`verify.sh` 接受相同參數，`PYTHON` 可指定本機 Python。上例以本案目錄為相對位置，請依 checkout 指定實際腳本路徑；支援原始 `apk-analysis/tsl9-...` 及交付後 `analysis/...` 版面。

實際檢查成功會輸出 `actual_native_artifacts_read=true`、`actual_call_frontiers_checked=true`；僅中繼資料檢查則兩者皆 false。檢查器自行讀取 ELF、物件、反組譯、IR，不依 producer 的 `passed` 欄位代替檢查。重播需要同一批實際產物及相同韌體讀取模式。

完整前綴、632 位元組全區所有權（含剩餘八個可執行位元組）、原始 ABI 准入、映像配置、安裝中 ROM、中斷、硬體及 OTA 相容性仍未證明。本審查不把既有元件升格為已整合韌體。
