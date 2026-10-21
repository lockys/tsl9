# OTA 頁面回覆：原始指令與契約

[English](readme.en.md)

本次只核對原始 ID2966 V4.1.60 的 `0x9B8E..0x9C0A`：共 124 bytes、50 條 RV32I/C 指令。`source-proof.py` 獨立拆解指令欄位，逐一比對操作數及順序，不解譯指令、不執行韌體。18 個操作數或順序錯誤案例均由指令契約拒絕，並非只依賴完整映像雜湊失敗。

`source-proof.json` 保留已完成的原始 carrier 讀回結果。`retained-evidence.json` 只保存先前協定分析與原始 8280 筆 RELA carrier 中相關的原始指令、符號及重定位證據。原始映像 SHA256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；本段為 `5171c6d96b0151461524f4719cc96d8151e0fec5196a591d5ecc516b82a15198`。

## 已確認的流程與邊界

`contracts.json` 逐一記錄保存順序、即時指標讀取、呼叫參數、位元組寫入、重新讀回的堆疊資料及終止路徑，附上原始 PC。入口 A0 是不透明 context，A1 是不透明 command，A2 是**完整 32 位元 index**。`9BAC` 直接將 A2 存入 S1；只有封包標頭取低16位元，複製來源仍使用當下 S1 的完整值：`u32((0x20004 + S1) << 10)`。將 C 介面直接改成 u16 會縮窄原始入口契約。

`9B8E` 配置32 bytes堆疊；先保存 S2，再於 `9B96` 讀取配置函式指標，之後才保存其餘暫存器。`9BAE` 以 A0=1026 呼叫該指標。回傳零才跳到 `9BFA`，重新讀取六個堆疊欄位、增加當下 SP，再經剛讀回的 RA 返回。A1..A7 是不透明配置函式留下的值，不能補造共同狀態碼。

非零路徑中，`9BB6` **先**將 index 低位元組寫到 allocation+1，`9BBA` 才將高位元組寫到 allocation+0。`9BC2` 從當下 S2+0x4C 重新讀取複製函式指標；`9BD4` 要求從數值來源複製1024 bytes到 allocation+2。`9BE0` 呼叫 `8A56` 的 TX，以當下 S3/S4/S0 及長度1026作參數。本段沒有依複製或 TX 的狀態碼分支。

釋放路徑是**尾端轉移**，不是一般呼叫後由本段回傳統一結果。`9BE4` 先從當下 S0 選出 A0，`9BE6` 才還原 S0；`9BE8` 先從當下 S2+0x68 讀取釋放指標，之後才還原 S2。接著重新讀取 RA/S1/S2/S3/S4、將當下 SP 增加32，於 `9BF8` 透過 T1 跳轉而不更新連結。A1..A7 是 TX 留下的值；最終是否返回及回傳什麼，由釋放函式決定。

每個堆疊存取都使用當下 SP；函式指標使用當下 S2；呼叫後仍使用當下 S0/S1/S3/S4。不透明被呼叫函式可能修改暫存器、透過別名修改堆疊、轉移或永不返回。保留 SP/S 暫存器只能是特定 native profile 的**前提**，不能當成本段已證實的事實。重新讀回的保存值可能不同於最初寫入值。原始程式沒有攔截空函式指標；空指標與「配置函式回傳零」是不同情況。

半字 `8297` 的獨立解碼為 C.JALR **rd=x1、rs1=x15**；舊資料中的 ESIL 將返回位址寫入 A5 的敘述不正確，本檢查不使用它。直接指令寫入的暫存器集合與不透明呼叫的影響分開記錄，不能據此宣稱其他暫存器被保留。

## 符號、參照與可攜驗證

原始 section 是 AX/PROGBITS、對齊2、長度124；公開符號 `__tsl9v4160_ota_code_9b8e` 是 GLOBAL NOTYPE、size0，沒有既存的 canonical FUNC124 provider。兩筆內部重定位分別代表空配置分支與 TX JAL；一筆外部 RVC_JUMP 位於 `9DF4`，指向入口 offset0，是 W/R 共用的實體尾端路徑。空配置區域標籤位於 offset108。本 carrier 沒有已記錄的外部重定位指向該內部標籤；計算、編碼或 ROM 內部參照仍未知。後續整合必須明確保留或取代這些角色。

由專案根目錄執行；引用的唯讀 ELF parser 同時支援發布版 `analysis/` 與工作區 `apk-analysis/` 路徑：

```sh
python3 -B apk-analysis/tsl9-v4160-ota-page-reply-2026-10-22/source-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

shell wrapper 接受相同參數，需要時設定 `PYTHON`。預設重新檢查指令、18 個錯誤案例及 source-manifest／保存角色綁定，明確回報**沒有重新讀取實際封存 carrier**。加上 `--object ORIGINAL.o` 才會使用已固定雜湊的可攜 ELF parser，重新讀取實際相關符號與重定位。歷史保存結果與本次實體封存檔讀回是不同證據層級；發布 seal 不包含產生的 build object。

這份 source-only seal 不證明重建 C/C++ 的行為、native 固定位址整合、精確中斷／故障前綴、已安裝 ROM／BOOT 身分、硬體行為或藍芽更新相容性；仍需要各自的實作及整合證據。本輪沒有目標程式執行、模擬器、網路請求或實體 I/O。
