# Allocator callback word 的設定來源

[English](readme.en.md)

**已找到實際的條件式寫入來源：候選初始化函式複製的 64-byte 設定區，其中欄位 +52 正好是 allocator 讀取的 callback word。** 因此只找絕對地址 SW，或只看到啟動清零，都不足以描述這個 word 的生命週期。尚未證明此欄位在真實裝置上是零、指向哪個函式，或不會觀察 ambient A2。

本輪只讀取既有兩個 SDK sparse HEX／segment、官方 ID2966 與既有封存證據。沒有下載、編譯、執行／模擬 RV32、操作硬體，亦未產生 provider／BIN。

## 真實 byte 與條件式地址關係

| 項目 | V1.40 / carrier | V1.31 / carrier-dec2023 |
|---|---|---|
| Slot 400A4 的實際 word | 43D0A | 43C7E |
| 本輪初始化前綴 | 43D0A..43D7C，114B／41 指令 | 43C7E..43CF0，114B／41 指令 |
| S0 設定基底 | 20003000 | 20003000 |
| 複製目的地（S0 保持數值的條件下） | 2000323C | 200031EC |
| 目的地 +52 | **20003270** | **20003220** |
| Allocator 讀取目標的 word | 20003270 | 20003220 |
| 清零 helper 來源 | Flash 402D2..402F0 | Flash 40292..402B0 |
| 映射的清零 helper | RAM 20000022..20000040，30B／9 指令 | 同左 |
| 條件式零初始化範圍 | [20002F48,20003668) | [20002EF8,20003618) |

候選的 word-copy 映射、原 sparse HEX 與 segment 雜湊都重用並驗證已封存 resident-entry／allocator-review 的來源鏈。原 Runtime SHA256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；本輪亦實讀其 13B4C..13BA6 的 90B，確認原 App 在 allocator-like 呼叫13B68之前仍以 A2 傳來源指標。

## 設定區的 bulk copy 是 writer

初始化前綴先檢查傳入設定指標所指向的資料，將設定指標放到 S1，且在複製前已有一個數值目標200004BC的呼叫。成功分支設定 S0=20003000，再執行：

1. V1.40 在43D5A設定 A0=live S0+23C；V1.31 在43CCE用+1EC；A1=0，A2=64。AUIPC/JALR 對的數值目標是2000039C，與兩個候選 slot40048 的實際 word相同。這裡只證明清零**請求**，沒有假造函式已正常完成或保存所有暫存器。
2. V1.40 在43D66..43D74重新設定 A2=64、A1=live S1、A0=live S0+23C並呼叫20000332；V1.31 的對應點43CDA..43CE8使用+1EC。此數值目標也等於兩個候選 slot4004C 的實際 word。
3. 20000332的58B／18指令 forward-byte-copy body已在舊 compact/callee-review封存，沒有 opaque nested call。其 source LBU 先於 destination SB，故在正常返回、有效映射／profile、live S0/S1保持合適值、無干擾／不利 alias 等條件下，設定區 +52..55 的四個依序讀取位元組寫入 allocator 的 callback word。

這不是原子 READ32 的快照或無條件參數保存保證。先前的呼叫、MMIO、記憶體回應或中斷可影響 source、destination、SP、S 暫存器與實際內容。指標來源是 **live S1**，不能自動等同 entry A0。欄位的 SDK 名稱／原 App 如何建立其內容，由獨立設定區證據處理，本輪只確認原始碼的 +52 關係。

本輪在 copy 返回後的目的地 ADDI 停止；沒有審查後續整個初始化函式或重建整份 ROM。之後的函式、間接呼叫、bulk write、外部程式或非同步事件仍可能更新 callback word。下一層真正 callback 函式身分與參數使用尚未取得。

## 啟動清零不是永久 callback 身分

每個候選另重讀30B清零 helper，以及原初始化末端8B AUIPC/JALR tail。數值目標為 RAM20000022；helper 以 unsigned A4>=A5 比較、每次 WRITE32 zero並+4，包含最後一個 word。上述 callback word完整落在其範圍內。

這只證明**若**該候選的啟動流程、複製映射與清零正常完成，該次零寫入會涵蓋 callback word。它不代表已安裝身分、當前值或之後維持零。設定區 bulk copy 就是一個後續 writer 的具體證據，不能再以零初始化排除 allocator 的未知回呼。

## 有界參照盤點與反例

只在兩個已保留的連續 segment 逐 halfword offset搜尋指定標準編碼：相鄰 `LUI reg,20003` 加 `LW rd,wordOffset(reg)`，各12組；同一種基底的相鄰標準 SB/SH/SW 直接覆蓋 word有0組，LUI/ADDI精確取地址0組，任意 byte offset的完整 U32LE地址 literal也0組。這是**語法 pattern 盤點**，不是全 ROM 指令邊界、可達 CFG、computed references 或寫入缺席證明。前述 bulk copy正好說明其限制。

`ledger.json` 保存每組8B原始欄位與來源 PC，而非複製整份 ROM。額外 decoder只補本輪實際遇到的標準 C.AND、標準32-bit JALR，以及候選 Xwchc QK_C_LHU 欄位；Xwchc定義來源由前輪已pin LLVM TD驗證，並未聲稱真實晶片支援已被量測。每候選四個實際 single-field byte反例：複製目的地、64-byte長度、啟動 store值、callback load-offset；共八個均拒絕。沒有重跑舊 HOST 矩陣或 ISA 狀態。

## 重跑與證據界線

```sh
# 只有 metadata／封存來源依賴；不讀原 BIN 或候選 body
python3 -B check.py --project-root ROOT

# 兩參數須一起提供，才實讀原 App 與兩個既有候選
python3 -B check.py --project-root ROOT \
  --firmware ID2966.bin --candidate-root EXISTING_WCH_REFERENCE
```

預設 `metadata_only=true`、`actual_original_firmware_read=false`、`actual_candidate_sources_read=0`；顯式檔案則 false／true／2 並重跑八個反例。工作區 `apk-analysis/tsl9-*` 與交付 `analysis/*` 都能解析，不依賴歷史 build。`capture.py`僅 create-only 保存有界 operand資料。

已安裝 resident、callback function/lifetime、App實際零值、ambient A2無關性、完整 ABI、實體 Flash／NV 所有權與 OTA相容性均未證明。ABS40000仍只是數值 witness，不是已安裝 provider。維持 full8 與未知 callee 邊界。
