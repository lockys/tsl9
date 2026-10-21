# TX 0x8A56 的獨立 ABI 與靜態元件審查

[English](readme.en.md)

目前可讀 C/C++ 元件為 280 bytes、96 條指令，大小符合原函式範圍；**尚未證明原始 ABI、原位置替換或完整映像整合成立**。本輪保留既有 12 個可讀函式的完整映像，不把這個 TX 元件放入其中。

`summary.json` 記錄最終選定的來源、產物與審查收據雜湊。`selected-c.json`、`selected-cpp.json` 是本輪實際讀取物件、LLVM IR 與連結元件的審查記錄；它們不會使預設檢查自動存取當時的 build 目錄。所有封存成員均為來源或中繼資料，不包含編譯產物。

## 原始證據與已確認邊界

官方 ID2966 V4.1.60，base `0x8000`，函式 `0x8A56..0x8B6E`，完整 280 bytes。`original-source.json` 保存實際原始證據；`original.py` 可重新核對指定韌體與選用的原始 carrier 物件。九個已記錄外部入口都是函式起點，其中八個建立 RA，一個 `0x13EAC` 為 JAL rd0。`0x135A8` 是 JAL rd1，RA 為 `0x135AC`。不依 relocation 類型或符號名稱猜測是否連結。

原始的 unsigned `length > 1039` 檢查位於配置 frame 之前。程式使用兩次 ROM `+0x13C` 指標呼叫；這些呼叫的實際簽章、保存規則及硬體效果均未知。第二次呼叫的 A2/A3 必須沿用第一次 opaque 呼叫留下的值。選定 lane 後以 1062 為 stride，組出 header、逐 byte 複製與 checksum，最後寫入 descriptor，再透過 ROM `+0x50` 的指標 JR T1，不建立新的 RA。這裡沒有看見 alloc/copy/free 呼叫。

初始長度上限不能證明 opaque 呼叫改變 S0 後仍有相同上限。迴圈以低 16 位 counter 與 live S0 比較，索引地址使用完整 counter。任意 ROM、非法記憶體、非返回、GP/SP 改變及非同步中斷的行為沒有實機證明。

## 目前 C/C++ 的具體差距

- 編譯器先減 SP 並保存五個暫存器，才檢查上限；原程式的大長度路徑直接 RET，不存取 frame。
- 第二個 opaque 呼叫位於函式 `+0x62`，原程式是 `+0x5E`；返回位址與內部控制位置不同。
- 成功路徑的 RA/S1/S2/S3/S0 還原延至 descriptor 寫入與 task byte 讀取之後；原始程式穿插還原。fault、frame alias 或中斷前綴不能宣稱等價。
- 正規化分支目的地與 PCREL immediate 後，指令集合仍不同，包括 BEQ/BNE 控制結構、MUL/ADD 運算元與 GP 地址形成。它不是只重排現有指令就可修復的候選。

目前已確認第二呼叫前沒有新增 A2/A3 寫入、沒有額外的 failure A1 copy、沒有用 A7 快取 loop length，並會讀 live S0。這些改善不會消除上述差距。

## 驗證方式

預設僅驗證封存來源、中繼資料與相依來源雜湊，不讀韌體或 build 產物：

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/check.py --project-root .
```

明確指定新編譯產物與本機韌體，重新執行實際靜態檢查；收據必須是尚不存在的路徑：

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --folder /absolute/native/c --receipt /absolute/new-review.json
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/ABI-review/review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin --replay /absolute/new-review.json
```

`review.sh` 無參數執行中繼資料檢查；傳入參數時轉交 `review.py`。可用 `PYTHON` 選擇 Python 路徑。實際檢查 stdout 的 `actual_build_artifact_replay` 為 true，但 `original_ABI_admitted` 仍為 false。

每個語言模式均對 96 條實際指令逐 byte 解碼；七個原始運算元變異與兩個實際連結 ELF byte 變異會被拒絕。物件僅有原 RAM alias 的 PCREL HI/LO；連結 witness 的兩個編碼指令解析到數值 `0x2000B18C`，其餘 bytes 與新編譯物件一致。數值提供者不是已安裝 RAM、ROM 或板型證明。沒有執行 RISC-V、模擬 ISA、產生新 BIN、通電或燒錄。
