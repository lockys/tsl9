# 35 個條件回呼與必要本體的原生重建

本輪是離線 C11／C++17 重建增量，沒有可燒錄 BIN。來源仍為 ID2966／伺服器標示 V4.1.60 的候選映像，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；標籤本身不證明原硬體適用性。

## 新增程式與身份

[共用 C/C++ 原生來源](src/materialized_callbacks_native.c) 捕獲 35 個已由消費端證明用途的條件 callable，以及 8 個必要直接被呼叫入口，共 2,658 B／44 個實體程式片段／865 條指令。直接 closure 包含10556、AB5E、FA3C、FA4A、FAFE、F838、B5C6、17CB2。A4CC／A4D8 的遠端共用冷區段分開配置，不填補約10KB span 中的空洞。原先已存在的程式保持原 storage；FD6A 的實際 NOTYPE0／size0 code view 也保留，不強改 FUNC。

59 個原 materialized-only 義務已完整盤點：35 個條件 callable、5 個資料讀取但 extent 未閉合、3 個可變資料指標但生命週期未閉合，以及16 個未知參數／欄位。callable 分類根據實際寄存器傳遞、條件呼叫或 registry slot+4 的儲存及間接消費。例如1056E等經1083C／10846或107C6／107D6呼叫；10630等經9124註冊、901A／9058消費。未知 ROM 參數沒有因為位元組似 code 就被當成函式。

35 個原 canonical 取址符號仍是 NOTYPE0／size0，實際 captured FUNC helpers 分名。新增提供者合計83＝43 FUNC＋36 NOTYPE＋4 OBJECT；其中多出的一個 NOTYPE 是新揭露的1A4F4讀取基址。這些 metadata 與 raw CFG 不證明原 C prototype、完整邏輯函式 extent、任意動態 caller 或原機 ABI。

## 首次未遮罩計數器的讀域

10630 的原始指令在10648將一個 LBU 值布林化，再於1064E乘17；1066E先讀 `base+{0,17}`。10676另外 LBU 一個 counter，1067C讀 `base+17*bool+counter+1`，到10686才對遞增後的 counter 做 AND15。因此不能假設首次 counter≤15或縮成34B；保守本地讀域是 `[1A4F4,1A606)`，274 bytes。這是由原始讀取指令導出的有限域，不是原 C 物件大小或硬體上的實際執行觀察。

其中1A518／1A528／1A538各15B已存在，保留原 section、flags、bytes、OBJECT15及 NOTYPE0。只新增以下四段原始資料：

| 新片段 | Bytes |
|---|---:|
| `[1A4F4,1A518)` | 36 |
| `[1A527,1A528)` | 1 |
| `[1A537,1A538)` | 1 |
| `[1A547,1A606)` | 191 |

新229B加舊45B形成完整七段274B聯集，無重疊或缺口。兩個1B片段是此讀域需保留的原始資料，不能拿 linker padding 代替。canonical1A4F4只綁首段 OBJECT36 的 NOTYPE0 起點，沒有虛構 OBJECT274 或重配舊資料。它是新本體才揭露的義務，不是前輪60 UND之一。

## 整合與驗證界限

新 spec 繼續使用未修改的 `verify-data-anchor-extension.py`（SHA256 `53e98521e679f5e2db9c687932f52e95787ebeafbeb8f019c8aa4efcc0954cbe`），完整 fresh 重播既有 callback baseline，保留前輪 RO7／data anchor，再加入本輪 native module。原92個 guards及前輪 typed-anchor gates 保留。該 frozen engine 的 consumer proof 只掃舊 baseline549；本輪不能把 CLI PASS 冒充新增程式的完整 ingress 證明。

新增程式、材料化、known direct／relative／self-PC 入邊、1AB58及10630讀取前提，須由本輪獨立合併後 audit 另外核對。交付器要求最後 `current_anchor_ingress` 證書，並以目的目錄實際 object／witness 與已審查 W 產物逐 byte 相同，連結到交付內容；不宣稱 frozen CLI 本身涵蓋新增入邊。

完整 ROOT fresh receipt：`build/data-anchor-extension-de76ad7bf40a4255b34fffe96032ec85/verification.json`，SHA256 `acb8df0bcef0e3d104c9c2b79735811d664fa6a8c44d0e7742b23127f77c8865`。

| 累計項目 | 實際結果 |
|---|---:|
| code／RO | 55,908 B／3,244 B |
| 檔案 payload／非空 allocations | 59,152 B／598 |
| semantic RELA | 6,672（本輪增加370） |
| module providers／code views／data anchors | 623／2／1 |
| relative32 expressions／RAM views | 534／27 |
| strict 真 UND | 25（仍 fatal） |

C11／C++17 merged object 都是 `a5c2562dc80f12699932222e36014ca3a0fe61423404d685d41bfc14cb9ddcc2`；numeric witness 都是 `588ad67c793a68c963e3344608e3b887b7c2a7ecc8d91e8c9d83df00c18035e3`。witness 僅檢查原數值配置，不供應剩餘依賴，不能當 firmware。

Standalone canonical receipt：`native/build/b42f6ce3796e433c896c9eaac22d18b0/verification.json`，SHA256 `09f3d31209b83b76d68f5fc147b497d7b50d73dcf097197b809b15d849d7a136`。每語言49個實際 ELF 反例均拒絕，合計98個；包含36個原 NOTYPE 身份逐一改 FUNC、captured FUNC改 ABS、callee／RAM改 ABS、HI／LOW、RO改 byte與虛構 OBJECT274／額外 storage。68個 standalone UND都是既有 provider／RAM／view 引用，不能與25個完整整合 UND混為一談。

執行 `python -X utf8 -B verify-data-anchor-extension.py --spec evidence/materialized-callbacks-integration.json` 可從本專案來源 fresh 重建。目的目錄 `analysis/v4160-materialized-callbacks-2026-10-20/destination-verification.json` 才證明當地交付結果。實體 MCU／PCB、ROM／BOOT／IRQ／stack／記憶體、必要功能等價性及原藍牙 OTA 接受條件仍未證明；strict 保持 fatal，所有 readiness 為 false。
