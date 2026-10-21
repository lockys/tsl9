# 原檔唯讀資料與十二個資料位址

本階段在既有 C11／C++17 原生工程中加入 21 個實際唯讀陣列，共 285 bytes，並將十二個原始 AUIPC／ADDI 資料指標綁定到實際區段內的精確 offset。這些是原 ID2966 V4.1.60 檔案中的資料，沒有新增程式指令、stub、來源外資料或跨版本內容。這是原生資料儲存體與位址解析的進展，不能據此宣稱原機執行或可藍牙燒錄。

來源檔案為 76800B，原始 VA 範圍 `[0x8000,0x1AC00)`，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。它仍是下載取得的候選映像，未經實機讀回證明為板上目前執行的內容。

## 新增資料的證據邊界

原始 `0xCF5A` 的 byte load，其 base 為 `0x1A078`。對相鄰原指令逐步推導，可構成全部 4096 個局部潛在 offset；這不是硬體觀測，也不證明全域可達性、alias 安全或完整執行讀域。來源與這個局部讀域的交集為 `[0x1A078,0x1AC00)` 共 2952B，其中 2691B 已保留，本輪補入缺少的 17 個區間共 261B。`0x1A668` 與 `0x1A674` 的十二 byte record views 在其中分開為真實陣列，不重複供應 bytes。

另外補入 `0x19DE0` 與 `0x19DFC` 各 12B 的已觀察三 word 視窗，總新增 285B／21 sections。private `OBJECT` size 只表示本輪陣列實際儲存大小，不是恢復了原始 C 物件邊界或 resident 完整讀取範圍。

三個局部潛在讀域分別為 `0x1A078 + [0,4096)`、`0x1AAE8 + [0,1024)`、`0x1AB48 + [0,512)`。後兩者是第一個讀域的子集，來源外聯集仍有 1144B 未提供。這不是整個程式讀域的上限；opaque resident、逃逸指標、IRQ 與 alias 仍有其他未知。不得因目前來源中沒有資料而補零或縮小索引。

四個保留的三 word 視窗使用原始 VA 固定語義，無新增 R32 relocation：

| 原始 VA | 三個 word |
|---|---|
| `19DE0` | `8B90, 0, 85C8` |
| `19DFC` | `0, 888C, 0` |
| `1A668` | `10D30, 10D2E, 0` |
| `1A674` | `10C36, 11544, 10C34` |

八個非零值均核對原檔與實際 code section 的 private instruction anchors；四個 null 保留。reference V1.31 的部分 resident 消費者是條件性參考，不能取代原機 resident 身分、生命週期或 ABI 證明。

## 位址綁定與實際原生驗證

十二個 canonical 標籤：`19DE0,19DFC,1A078,1A0D8,1A430,1A454,1A478,1A638,1A668,1A674,1AAE8,1AB48`。其原指令各有唯一 HI20／addend0 與自身 LOW12_I，標籤是 GLOBAL／NOTYPE／size0，定義於真實 RO section 的精確 offset，沒有 ABS provider 或假函式。

正式 W 收據：`build/retained-data-extension-3d426088c0054523ac9c7de854e10e8a/verification.json`，SHA256 `cbdd8d63e127be93558b8c6d441e2810ad05bf0b4375ec6b691a4b3e24055805`。

- 從完整舊 660-section／13-UND 階段 fresh 重建，繼承來源與舊 verifier 保持原樣；新增後 681 個非空 allocated sections。
- 新 unit 恰為 285B RO、零指令、零 UND、零 RELA。原 8280 筆 raw RELA 的 site、type、signed addend、multiplicity 保留，只准十二個原資料地址的 referenced-symbol role 從 UND 轉為真區段標籤。完整數值語義仍相同。
- 每個已納入 code／data byte 的原始 VA、大小與內容均從實際最終 ELF 核對；舊 bytes、17 word table 與四個 record 的原位址語義保持。
- C/C++ 的 unit、merge、bound object 與數值 witness 分別完全一致。bound SHA256 `1bd73c6ac3577dadc86b0cd4ea3e52764108010450abc8f96270dd9045e91d79`；witness SHA256 `7a54eba3ed510d780dcf3c490e6c0c4d1019deb56e70744c026247894afad9cc`。
- 每語言 16 個真實 ELF 內容反例及 3 個 metadata 反例均被拒絕，包括假 ABS／FUNC／OBJECT、錯 offset／size／bytes／flags、HI addend／LOW 破壞、等值但錯誤的 raw relocation role、被引用的新增 SECTION、SECTION visibility 與繼承 SECTION metadata 改寫。
- 原檔已納入 76705／76800B，仍有 95B 未納入；其中 41B 位於 file-backed LOAD 間隙，28B 與原檔不同，另 54B 未被 file-backed LOAD 覆蓋。這是檔案儲存體的證據，不是功能完成百分比。

最初整合失敗於驗證器對最終 symbol metadata 的假設，失敗來源與差異保留於 `analysis/v4160-data-addresses-2026-10-21/integration-debug/`。實物顯示 unit 沒有新匿名 SECTION，partial merge／binding 各產生 21 筆，而 final link 省略這些未被引用的新符號。修正只容許由新 RO allocations 差集推導的 21 筆 exact LOCAL／SECTION／空名／value0／size0／other0 metadata，按各 RELA 的實際 `sh_link` 與 symbol index 證明無引用；另有一筆精確的非 allocated `.comment` mapping marker 明示省略。所有舊 metadata 及其餘 final symbol Counter 仍精確驗證，不泛化忽略 LOCAL／SECTION／ABS。

## 未完成項目及重建方式

嚴格 final link 仍因 `__tsl9v4160_rom_entry` 缺少實作而失敗，沒有 strict executable 或 BIN。`ADDRESS-WITNESS-ONLY.elf` 只為該地址義務給數值 `0x40000`，未供應 resident 程式或 ABI。

十項 callback runtime 契約與十二項資料 runtime 契約仍列為未知；ELF UND 數量不能當成執行契約完成數。原機硬體 SKU、實際 ISA／resident、ROM／RAM／stack／IRQ、Flash／BOOT 與原藍牙 OTA 接受條件亦尚未證明。本輪沒有執行原始或重建 RV32、ISA 模擬、硬體 I/O、vendor API 請求、BIN 輸出或刷寫。

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-retained-data-extension.py --current-receipt <實際13-UND收據絕對路徑> --proof-root <本輪證據資料夾絕對路徑>
```

命令只編譯、連結與檢查，會建立新 build 目錄。獨立審查與目的地交付是否完成，應另核 `analysis/v4160-data-addresses-2026-10-21/integration-review/`、同層 `destination-verification.json` 及 W 的 postdelivery-readback 收據，不能僅引用本 W 建置收據。
