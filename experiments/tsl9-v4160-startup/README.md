# 最新整合：取址引用與回呼本體

執行 `python verify-extension.py --spec evidence/materialized-integration.json`，詳見[MATERIALIZED.md](MATERIALIZED.md)。本輪新增七個本地程式capture（1812B）及3B已證local-read範圍；整合6306B code、459B RO、554筆semantic relocations。五個原opaque程式名稱保留NOTYPE0 view，不宣稱原C型別／ABI；84個UND與79處間接callsite仍未閉合，沒有可燒錄成品。

---

## 前一階段：初始化第一層與持續執行流程

該階段執行 `python verify-extension.py`，詳見[CORE-FLOW.md](CORE-FLOW.md)。它加入19個本地本體／2788B，含初始化呼叫鏈、全部第一層callee及主迴圈；整合4494B code、456B RO、437筆重定位。該scope嚴格link仍拒絕79個不同角色的UND，另有48個間接callsite的target／ABI待確認；沒有可燒錄BIN。

---

## 前一階段：main 與七個直接呼叫入口

該階段入口是 `python verify-dependencies.py`，詳見[DEPENDENCIES.md](DEPENDENCIES.md)。它加入18B main及366B真實callee bodies，合計1706B code、456B RO、223筆relocation；該scope三個明示UND為8180、9250及ROM40000，動態回呼與硬體／OTA契約另保持未知。下方原有vector／clock／reset說明各自屬先前獨立驗證階段。

---

## 先前階段：vector／IRQ／clock

此階段入口為 `python verify-vector-platform.py`：reset、真clock、有限vector capture與IRQ本體，共1322B code／456B RO／211重定位；該階段九個真實callee依賴仍使嚴格link失敗。C11與C++17靜態核對通過，**尚無可燒錄BIN**。[該階段範圍與三個驗證入口](PLATFORM.md)。

---

以下保留初始reset-only階段的範圍說明；其`verify.py`仍只驗證該元件，四UND不當作最新整合結果。`verify-platform.py`則是clock-only三UND階段。

## 初始reset-only C/C++ 元件

從固定來源 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的真實 BIN，重建138B reset入口、128B初始化資料與35160B NOBITS RAM carrier。程式為 C11／C++17 加 RV32 inline assembly；Python只負責離線取證與ELF核對。這是新版獨立元件，不替換原R81／V4.1.00工程，不是可燒錄韌體。完整產品選項文字未保留，ID2966對使用者這顆硬體的適用性仍未證實，不能只憑V4.1.60標籤認定。

## 已從原始指令確認的地址模型

| 項目 | ID2966／V4.1.60 | 舊ID2581／V4.1.00 |
|---|---|---|
| reset 模型位址 | 0x186AA | 0x183FE |
| GP地址 | 0x20004000 | 0x20004000 |
| 初始化來源／長度 | 0x1AB60／128B | 136B |
| data／BSS分界 | 0x20004080 | 0x20004088 |
| BSS清零終點 | 0x2000C958 | 0x2000C950 |
| 數值RAM carrier範圍長度 | 35160B | 35152B |
| BSS清零長度 | 35032B | 35016B |
| 初始SP地址期望 | 0x20010000 | 0x20010000 |

`evidence/startup-evidence.json`記錄22份映像的來源hash與獨立地址運算。基址由offset0x40的vector值減去已核mret stub的file offset導出，再與offset0x38核對；沒有以r2的-m選項證明載入位址。以上不是實體RAM容量、stack有效性或MCU型號證明，也不能從共用GP/SP推論兩版可混用。

## 原生表示與驗證

`src/startup.c`保留原138B指令ABI，加入14筆語意重定位（6組own-anchor PC-relative pair及2筆JAL）。128B初始化來源只配置一次；RAM是一個NOBITS物件。SP是size0的ABS位址常數，沒有配置stack。初始化資料目前保留原始bytes，其中raw指標的型別、被指物件與後續使用尚未全部整理，不能以此宣稱完整依賴閉合或可任意重定位。

執行 `python verify.py`；預設使用`../../firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，也可給`--firmware <絕對路徑>`。使用本機已存在的Windows Python及Android NDK27.1.12297006 clang／lld，沒有安裝或網路操作。

驗證C11、C++17的RV32物件逐byte相同，核對138B原指令／128B原資料、NOBITS extent、size0 SP與14筆重定位。嚴格最終link必須失敗，且不留下ELF。輸出的唯一正常native產物是relocatable object；沒有BIN。

另有明標`ADDRESS-WITNESS-ONLY.elf`的**數值位址驗證夾具**：`layout/address-witness.ld`只把四個已解出的數字填入linker symbol，讓靜態工具比較原指令重定位後是否逐byte相同。四個數字沒有對應實作，未供應向量表／clock／main／ROM程式，也不代表實體位置可呼叫。此ELF只供byte核對，不能當候選韌體、不可執行或燒錄。

## 尚缺條件

reset的四個明示外部依賴保持UND：vector_base（0x8038）、clock_init（0x1874A）、main（0x9008）、ROM入口（0x40000）。這是此元件的外部引用清單，不是完整韌體缺口總數。還需整理initializer中的指標物件、其他函式、ISR、BOOT/root、ROM版本／ABI、實體晶片／PCB／RAM／stack、最終配置及OTA相容性。沒有執行／模擬任何原始或重建RV32程式，也沒有操作硬體。

