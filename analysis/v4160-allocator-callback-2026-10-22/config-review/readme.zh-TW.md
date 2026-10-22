# 原 App 的 BLE 設定欄位與候選 header ABI

[English](readme.en.md)

本組只讀 ID2966 的 `0x199E2..0x19B16`（308 bytes）及兩份已保存的官方 SDK header。它不執行原機程式，不證明 call／MMIO 效果、實機 ROM 或 Flash 所有權。

## 實際編譯的結構欄位

以 pinned Windows NDK Clang 的 `riscv32-unknown-elf / ilp32` 分別包含 V1.40 與歷史 header，`config_layout.c` 的 `offsetof`／`sizeof` 均得到以下資料。兩個 object 各只有一個40-byte唯讀資料區段、零重定位／零真 UND／零可執行內容；沒有執行 RV32。

| 欄位 | 結構 offset |
|---|---|
| MEMAddr／MEMLen | 0／4 |
| SNVAddr／SNVBlock／SNVNum | 8／12／14 |
| staCB | 52 |
| readFlashCB／writeFlashCB | 56／60 |
| sizeof(bleConfig_t)／sizeof(status callback pointer) | 64／4 |

這是候選 SDK 的型別 ABI，不能僅由 header 宣告認定實機 callback 只讀兩個參數或不觀察 ambient A2。

## 原始 App 可見欄位

308-byte 本體的32個選定 instruction 欄位與23個標準 store 指令均以實際 bytes 核對；沒有宣稱完整解譯106個指令。

- 原函式配置96-byte frame。`19A20/19A2E/19A34..19A38` 請求 nominal slot40048，以 A0=當下SP+16、A1=0、A2=64 呼叫。不能只靠呼叫名稱宣稱零填成功，且先前 call 的 S0／SP 保留仍是條件。
- `19A3A/19A3E/19A42` 的 AUIPC／ADDI／SW 對 MEMAddr 建立數值 `0x2000418C`；MEMLen 的半字為 `0x7000`。
- `19A4A/19A4E/19A52` 建立 `0x08078000-1024 = 0x08077C00`，寫到 SP+24，即候選 config+8／SNVAddr。這是原碼設定數值，**不是全部 NV 寫入範圍或新增 `0x1AC00` 區域可用的證明**。後續未知 call、alias、SNV block default 與 Flash callbacks 仍需證據。
- 兩個明示 callback store 在 SP+72／76，對應候選 readFlashCB／writeFlashCB。原函式無明示 SP-relative store 覆蓋 SP+68..71／staCB；但中間有未知 call 與間接 store，不能推成 staCB 在 BLE_LibInit 時必為零，或之後永久為零。
- `19AE2..19AEC` 新讀 nominal400A4，以 A0=當下SP+16 呼叫。 [兩候選的真實 bulk-copy writer](../callback-review/README.md) 將 config+52 複製到配置 callback word，補上欄位來源，沒有補出實際 live 值。

五個反例只改 LUI／store／address／slot／staCB-overlap 的 immediate，先要求成功解碼且其他欄位完全相同，再要求語義 gate 拒絕。最初未封存的篩選器把無法解碼的變更也計入，已在 build 歷史保留說明並修正；舊封存證據與原始檔未修改。

## 重驗與限制

```sh
# 預設只驗本組文字／欄位 metadata，不讀原 BIN 或 layout objects
python3 -B check.py --project-root ROOT
# 實際讀原 App；另給 layout receipt 才重讀兩份 header/object
python3 -B check.py --project-root ROOT --firmware FW --layout-receipt BUILD/verification.json
# 明示兩份原 header，實際編譯只有資料的 layout objects
python3 -B probe.py --project-root ROOT --headers V140_HEADER V131_HEADER --tool-dir LLVM
python3 -B probe.py --project-root ROOT --replay BUILD/verification.json
```

`probe.py` 需要兩份實際 header，其完整 SHA 記於 selected metadata；沒有把 header 名稱當成版本證明。Python 介面可攜；本次 native compiler 為 pinned Windows NDK，沒有宣稱 Linux／macOS／CI 建置已通過。實際 readback 與 compile 日誌分開留存。沒有 HOST／RV32 執行、ISA 模擬、網路、裝置 ID、BLE／UART／CAN／Flash 或新 BIN。
