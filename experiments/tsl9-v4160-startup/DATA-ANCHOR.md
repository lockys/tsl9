# 1AB58 的已觀察讀域與獨立資料錨點

本階段完成離線靜態整合，尚未產出可燒錄的重建 BIN。來源是 ID2966／伺服器標示 V4.1.60 的候選映像，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；該標籤不證明硬體適用性。

## 實作與證據

新增 [C/C++ 共用資料模組](src/data_anchor_native.c)，只配置 `[1AB59,1AB60)` 的原始七個位元組 `334c667f99b2cc`。單獨編譯的模組只有一個唯讀 OBJECT7，沒有 code、UND 或 RELA，沒有為解除依賴而加入虛構引用。

原 `__tsl9v4160_address_1ab58` 以獨立的 `existing_data_anchors` 契約，綁在既有 `.rodata.tsl9v4160.readonly_view_1ab50` 的末端 offset8。實際 partial ELF 符號是 GLOBAL／NOTYPE／size0／default visibility，使用真實舊 RO section index，value8；原位址診斷 witness 中 value 為 `1AB58`。它不使用 ABS、不算新增模組提供者或程式位址視圖，也不配置儲存空間。舊 carrier 的八個 bytes、OBJECT8、型別、flags 與既有 view 均保留。

原始指令證據：F9F2 的 LBU 取樣、F9F6 的 AND7、F9F8 的零值退出，支配 F9FA／F9FE 的基址形成與 FA02／FA04 的單位元組讀取。因此在目前已知路徑，讀取偏移是 `1..7`。唯一 canonical HI／own-LOW 引用、目前已捕獲的直接入邊、534 個相對表項與兩個 self-PC 分派域均重新檢查，沒有已知的 guard bypass；兩條已知活指標後續路徑也由原始指令證明先覆寫指標暫存器。詳細 raw CFG、引用與限制見目的目錄 `analysis/v4160-data-anchor-2026-10-20/consumer-proof/contract.json`。

這些證據不排除任意動態 caller、別名、IRQ、context corruption、程式變異或不透明記憶體副作用。section-end anchor 不證明原 C 同一物件的 provenance；本模型沒有替 byte0 配置 section，但 LOAD segment／檔案 padding 仍可能覆蓋該位址，不能推論原 BIN 沒有該 byte 或實體位址 unmapped。

## 整合結果

新入口先完整重跑凍結的 `verify-table-extension.py --spec evidence/callback-bodies-integration.json`，再加入新模組。原驗證器、舊 spec、舊封存與所有既有程式／資料保持不變；原 92 個檢查保留。539 個既有模組提供者、2 個既有 code views、534 個相對表達式分別繼承，沒有重複計算。本輪增加一個 OBJECT 提供者與一個獨立資料錨點。

| 項目 | 實際結果 |
|---|---:|
| code | 53,250 B |
| RO | 3,015 B（本輪增加 7 B） |
| 檔案 payload | 56,265 B |
| 非空 allocated sections | 550 |
| semantic RELA | 6,302 |
| 模組提供者 | 540 |
| code views／data anchors | 2／1 |
| relative32 expressions／operands | 534／1,068 |
| RAM views／NOBITS bytes | 27／35,160 |
| strict 真 UND | 60（仍 fatal） |

完整 ROOT fresh receipt：`build/data-anchor-extension-62eb9a5b02134b3e98aed253d3c82cc6/verification.json`，SHA256 `7a679a95e4a07e12d3a72e1b1a363780801940d517c621774f843bd7eda3b4dc`。C11／C++17 merged object 都是 `409b69ab4d09c6a2a8d91c73305b60a72215ae4a99d85fe600dd4359c57f8e9c`；numeric witness 都是 `64efce9f3e0643acae2b23f5f2e612adcd423c379f3340180cfd28917283709c`。witness 只檢查原數值配置，未供應剩餘依賴的實作，不是 firmware。

Standalone canonical receipt 為 `native/build/ed5c9ae777274367a21290f257f8085e/verification.json`，SHA256 `d16b79f588d0f1ad7335760e8b765805a21cf64401ed96d2a0f19ed44101f1f7`；47 個實際 ELF／proof 反例全被拒絕。包含 ABS、同數值錯 section、offset7／9、FUNC／OBJECT／非零 size、hidden visibility、錯誤 fragment／byte0 補配、domain0／8、寬讀取、guard bypass 與遺漏引用。47 是該收據的總數，不是每語言各 47 個。

## 重播與完整目標

在本目錄執行：

```powershell
python -X utf8 -B verify-data-anchor-extension.py --spec evidence/data-anchor-integration.json
```

預設讀取專案中的下載候選 BIN；其他保留快照可明示 `--firmware`。新入口不依賴分析 scope 的 runtime sidecar 或 W 歷史 object 路徑。每次重播產生新的靜態 build 與收據，不執行或模擬 RV32。

實體 MCU／PCB、BOOT／resident ROM、記憶體／stack／IRQ、必要功能等價性及原藍牙 OTA 封裝／接受條件仍未證明。strict 最終連結繼續拒絕剩餘依賴，所有硬體／OTA readiness 為 false；沒有可燒錄的重建 BIN。後續問題見目的目錄分析資料的 `NEXT-WORK.md`。
