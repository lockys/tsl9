# Flash 入口順序與來源所有權審查

[English](readme.en.md)

本獨立審查核對原始六個 Flash 函式、已知 carrier 參照及新的可讀 C/C++ 入口順序版本，實際執行自有合成主機測試，並靜態讀取真正編譯的 RV32 產物。沒有執行 RV32 程式、連接硬體／原廠服務或啟動燒錄。

## 原始最後六位元組是有效指令

原始 ID2966 V4.1.60 SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；六個完整函式共 262 位元組、99 指令。`18F50..18F55` 的 `758f98cb8280` 對應 AND A4,A4,A3；SW A4,16(A5)；RET RA，完成最後一次即時控制器值的遮罩、寫回與返回。即使先前實作編譯為 94 位元組，也不能將這六位元組稱為 padding 或可用空間。

原始 program 在 18EF6 首次讀取控制器後，於 18EFA 對齊 A0，再於 18F00 首次寫回。新 100 位元組版本在相對 +4 讀取、+6 對齊、+14 寫回；原始對齊位於 +8。這改善了對齊與記憶體事件的先後關係，不代表保留原始對齊 PC 或每個指令邊界。

## 實際來源與入口參照

`source-inventory.json` 記錄實際掃描原始 8280 筆 RELA carrier（`646dbe43…edb97`）及先前 IRQ 整合後 8276 筆 RELA carrier（`9a5bd413…179b9`）的結果。少四筆是先前 IRQ 整合的變化，不能稱原始 carrier 有 8276 筆。兩者的六個 Flash 範圍位元組、符號角色及已納入參照完全相同，各掃描 24585 個已宣告指令邊界。

兩個清單均有 23 個直接參照及相符 RELA：17 個函式入口呼叫、六個同函式內的迴圈分支。18 個具名符號角色包含六個公開函式、六個 mapping symbol、六個私有迴圈標籤。私有標籤為 18EE0、18F02、18F0C、18F1A、18F2A、18F44，已納入的來向分支均來自各自函式內；此有限清單未發現外部指向內部／尾端的參照，但不能排除計算、載入、resident／ROM 或未知外部目標。仍有一筆未解 ROM relocation。

已知八個 9C0A 呼叫位置為 9D00、9E7A、12E7A、12F0C、12F6E、13078、130FC、1315E；包裝函式另呼叫五個 helper。獨立的 197BE resident callback wrapper 在 197C8、197CE、197D8、197DC 呼叫 helper。目前保留的 caller liveness 證據僅涵蓋先前已納入的 9D00 延續片段，靜態參照清單不等於證明每個 caller 的參數、延續或實際執行行為。

## 有界 C 變更與實際驗證

`check-review.py` 核對精確的新舊來源差異，不只核對新雜湊。program 改用相依的 fixed-A0 identity／alignment primitive、在前兩次輪詢後重新建立 fixed-A4 base，以及前兩次輪詢的 fixed-A5 遮罩。HOST 分支仍是原本純 AND 表達式，新增 base 操作只建立常數。公開標頭、主機 provider 與正式測試內容完全相同；主機 runner 只更換模型路徑，格式檢查與已審查版本一致。

沿用不可變的獨立預期效果 fixture，SHA-256 為 `d2387b7983052b2b3b863223eaf3873e00435a1bd03b5833ba31a4c7ad569705`，但已針對新核心重新編譯 C11、C++17。每語言均通過 12 情境、8964 項斷言，拒絕十二個實際編譯的行為突變；每個正常／突變執行檔均經目前格式 guard 在啟動前後核對，每語言合計 13 個。對齊控制改測新 HOST `FN_ALIGN0` 巨集，其餘十一項控制目的相同。這些是新版本的實際結果，不是挪用舊計數。正式主機測試另各通過 5 組／481 案例／247191 項檢查與六個編譯控制。

實際原生 C/C++ 元件均為 262 位元組、99 指令，其中 program 為 100 位元組、38 指令；ELF SHA-256 均為 `aeccc19da9c5764a386333dd26898429c35bf0ff40efb08c8f8417b11820339d`。`component-review.json` 獨立綁定真正新舊 ELF：其餘五個函式與前一元件位元組相同，僅 program 改變。靜態解碼器核對 A0 對齊先後、最後六位元組、目的暫存器集合與完整可達 CFG，並拒絕三個實際原生位元組控制。原始尾端另有三個語意控制，先前來源證據另保留二十項控制；這些均為靜態位元組檢查，不是執行韌體或主機編譯突變。

新 program 的五個迴圈目標仍位於原始相對 16／26／40／56／82；erase 的 18EE0 也不變。後續整合可依此真正 CFG 核對並移除／替換舊分支角色，不能只盲目維持數字 alias：原始 program 的 +8 目前落在四位元組指令內。初次控制器 scratch 改用 A2 而非原始 A5，後續 scratch 分配也有差異，因此未證實實體故障／未返回暫存器前綴、完整指令邊界或非同步等價；包裝函式先前的儲存順序差異也仍存在。

## 重驗與限制

```sh
python apk-analysis/tsl9-v4160-flash-entry-order-2026-10-22/source-review/check-review.py --project-root . --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

發布目錄入口為 `analysis/v4160-flash-entry-order-2026-10-22/source-review/`。預設唯讀核對目前來源、精確變更、保留結果及原始位元組；沒有編譯封存時，不宣稱重新讀取實際產物。提供 `--host-archive`、`--native-archive`、`--effects-archive` 可分別重驗保留的編譯封存；歷史 Windows 編譯器／工具路徑及執行檔格式須仍可用且相容。發布 seal 不包含 build 目錄、執行檔或突變來源副本。

最終原生 CLI 會將明確 `--firmware` 傳入編譯及重驗。保留的 CLI-options 結果記錄：用同一個固定雜湊映像的另一個本機路徑實際編譯 C、帶同一路徑重驗成功，以及錯用預設結果情境時拒絕通過。本審查在要求原生封存重驗時，也會向下傳入 `--firmware`；另可由保留的 program 位元組重驗三個靜態控制，但不宣稱讀取不存在的 ELF 產物。

`inspect-source.py` 可明確提供原始映像、原始 carrier、完整 layout、IRQ carrier 與結果路徑，以 `--reference source-inventory.json` 重跑完整參照核對；`inspect-component.py` 可明確提供新舊元件 ELF，以 `--reference component-review.json` 重驗靜態原生證據。`run-effects.py` 會新建輸出目錄，重新編譯並執行受格式 guard 保護的獨立主機測試，完全不呼叫舊未受保護的 runner。

來源所有權、自然符合大小的元件及主機測試，不代表完成整個映像的符號／layout 整合、ROM 實作、已安裝 BOOT 身分、Flash 持久化／時序／故障、硬體相容或 OTA 接受驗證。上層映像整合是另一道驗證。本來源審查沒有產生新韌體 BIN，也沒有實作新的產品功能。
