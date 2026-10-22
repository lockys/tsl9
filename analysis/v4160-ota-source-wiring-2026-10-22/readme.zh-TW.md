# OTA 原 caller 與真實 C/C++ 的完整實驗映像

[English](readme.en.md)

目標仍是原硬體可由 BLE OTA 更新的重建韌體。本輪完成實際原 caller 接線與完整實驗 BIN；**尚未驗證可刷寫，不應拿此映像測試原機。**

## 已確認的離線結果

- 同一 TU 包含既有可讀 OTA handler，並由編譯器建立真實強 FUNC568 別名；沒有地址代替函式、假 size 或新增 opcode 模板。
- 僅在既有 provider object 的副本弱化原 NOTYPE 全域入口；全部 691 個原配置保留。部分連結解析新函式的九個真實 provider，原 ROM 入口仍為真正 UND。
- 新 C 實際放在 `0x1AC00..0x1AE38`；原 caller `0x14094` 的 JAL raw `ef60d036` 到 `0x1AC00`，RA 為 `0x14098`。原 raw530 handler 保留；其原址不會憑名稱變成可讀 C。
- C11／C++17 產出相同 77,824-byte BIN，SHA-256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee`。繼承的76,800 bytes只有 caller 指令的三個 byte 改變。新增568-byte可執行C及456-byte明示非執行FF頁尾，不是用填充補缺失程式。
- 新物件僅承接 handler 接線；其餘大量區段仍是原始 carrier，不能當成全程式原始碼還原。

## ROM 數值見證與真 provider 的差別

原始 ID2966 的 `0x18730` JAL raw `6f70120d`，`rd=0`，數值目標為 `0x40000`。既有 reset section 位於 `0x186AA`，其 `+134` 的 type17/addend0 重定位指向真 ROM UND。完整 ELF 沿用既有數值邊界，角色為 ABS／NOTYPE／size0；這**只讓靜態地址見證可連結，不提供任何 ROM 程式或實機身分證明**。嚴格不帶此邊界的連結必須失敗，不能忽略未定義項或補 stub。 [原始欄位](original-ROM-boundary.json)

## 新縮小的 ABI 搜尋邊界

兩份官方候選的 slot `+0x70` 均指向 RAM `0x20000236`。每份讀取 wrapper86 bytes／35指令與 core prefix110 bytes／37指令；加上原 App caller90 bytes，證明 ambient A2 在 wrapper／prefix 未被覆寫，可流向從 RAM `0x20003270`（V1.40）或 `0x20003220`（V1.31）新讀取的未知 callback。這不是配置函式全程審查，更不是已安裝 ROM 身分。**仍不能證明新回覆 SP+6/7 與原 SP+12 的數值差異無害。** [實檔證據、八個欄位反例及停止點](allocator-review/README.md)

## 可重驗的內容

| 內容 | 證據 |
|---|---|
| 可讀 handler 與真同 TU 別名 | [模型](../../experiments/tsl9-v4160-ota-source-wiring/README.md) |
| 實際編譯、部分連結、完整連結與 BIN | [實作](implementation/README.md) |
| 獨立 ELF／符號／重定位／完整位元組核對 | [ABI 審查](ABI-review/README.md) |
| 候選配置函式的 A2 邊界 | [配置審查](allocator-review/README.md) |
| 可交付的實驗映像 | [BIN 說明](../../artifacts/offline-images/ID2966-V4.1.60-ota-source-wired/README.md) |
| 工作順序與剩餘條件 | [計畫](plan.zh-TW.md) |

所有執行均為本機靜態讀取、編譯、連結與萃取。未執行 RV32、CPU 模擬、BLE／UART／CAN、Flash 存取或廠商 API；未因接線改動重跑未變的 HOST 演算法測試。各 checker 預設 metadata 不代表實檔讀取，交付紀錄另外保存明示輸入的實際重驗。

## 仍未完成與新功能候選

實體晶片／板子、已安裝 ROM／BOOT、Flash／NV 所有權、RAM 邊界、中斷與完整 S／SP／RA／GP 契約、非同步觀察、OTA 格式／接受／失敗恢復尚未證實。原 BOOT 的數值頁上限包含新增一頁，也不能證明該頁可用或硬體相容。

值得新增的功能候選是**離線更新前檢查**：顯示候選 BIN 的身分、長度、各區段差異、未證明的 ROM／板型條件與恢復資料，讓人能辨識版本與證據不足。這是提案，尚未實作為原機功能，也不能用靜態檢查授予刷寫許可。下一輪先追查 fresh 配置 callback 或原 caller 的保存／回覆指標契約，優先關閉影響新 C 安全性的實際缺口。
