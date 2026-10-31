# 原 APP 的六筆 NVM 記錄與記憶體需求

[English](readme.en.md) · [設定／Flash 呼叫鏈](../tsl9-original-prebinding-settings/README.md) · [記憶體／ROM 合約](../tsl9-memory-rom-contract/README.md)

核對既有 C/C++ 的 7 個完整函式，共 **628 CODE bytes／189 指令**：initializer `0x131C2` 與六個 writer。原 BIN、兩份原位址 C/C++ 診斷 ELF 及兩個獨立 ELF reader 一致。新增的是可編譯的數值需求合約，**沒有新增可執行 target CODE、APP 整合或 BIN**。

## 原碼的讀取與寫入配對

| Record | 數值來源位址 | RAM destination | Copy bytes | Initializer guard | Writer | 額外 CPU source bytes 未證明初始化 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | `0x8077a00` | `0x2000c29c` | 112 | ASCII ×4 | `0x13138` | 144 |
| 1 | `0x8077900` | `0x2000c494` | 256 | `0x5A` at +255 | `0x12e54` | 0 |
| 2 | `0x8077800` | `0x2000c30c` | 256 | `0x5A` at +255 | `0x12ee6` | 0 |
| 3 | `0x8077700` | `0x2000c594` | 256 | `0x5A` at +255 | `0x12f48` | 0 |
| 4 | `0x8077600` | `0x2000c694` | 256 | `0x5A` at +255 | `0x13052` | 0 |
| 5 | `0x8077500` | `0x2000c40c` | 133 | `0x5A` at +132 | `0x130d6` | 123 |

每筆 read 的 RAM destination／count，均與對應 writer 的 source／count 獨立解碼配對。讀取順序如表；早期 read 在完整正常返回 CFG 中支配後續 read。fallback 仍是條件路徑，不宣稱每次啟動都會完成全部讀寫。

第一筆檢查 RAM `0x2000C2A8..0x2000C2AC` 的 4 個 ASCII bytes（32..126）。其餘五筆檢查各自最後一個 copied byte 是否等於 `0x5A`。這些 guard 都在自己的複製範圍內；**marker 相符不等同完整內容、CRC 或備份有效性證明**。尚未依這些數值給各 record 指派座椅／門鎖等功能名稱。

## RAM 與 NVM 數值範圍

六個 RAM buffers 共 **1,269 bytes**，數值區間互不重疊；總跨度 `[0x2000C29C,0x2000C794)` 為 1,272 bytes，其中 `0x2000C491..0x2000C494` 是 3-byte 間隙。它們均在原 reset 的 zero 區間 `[0x20004080,0x2000C958)` 內。這只證明編碼中的容納關係，不能證明物理 RAM、所有權、DMA／alias 或後續 IRQ 不會改寫。

六個 writer 的 destination 是相鄰且 256-byte aligned 的數值 pages，總範圍 **`[0x08077500,0x08077B00)`，1,536 bytes**。若另假設這些位址位於以 `0x08000000` 起算的連續平坦 Flash，所需 end offset 為 `0x77B00`（490,240 bytes）；**該 flat-map／容量假設尚未證明**。不能僅憑 literal 決定晶片容量、alias、ROM／data-Flash 角色或真實可寫區。

### 兩種候選擦除粒度

本機保存的 WCH CH32V20x [Flash 參考驅動](https://github.com/openwch/ch32v20x/blob/main/EVT/EXAM/SRC/Peripheral/src/ch32v20x_flash.c) V1.0.2 將一般 `FLASH_ErasePage` 註解為 4 KB，另將 `FLASH_ErasePage_Fast` 註解為 256 bytes；後者清除地址低 8 bits，以控制位 `0x20000`、啟動位 `0x40` 與 busy 位 `0x01` 進行操作。原 APP 的 `0x18EC4..0x18EF2` 重建程式也包含這組對齊、控制位和輪詢；這是靜態指令與候選驅動的對照，並不證明實機控制器或完整 API 相同。

六筆目的位址各自落在不同的 256-byte 數值區間，但全部同在一個按 4 KB 對齊的數值區間 `[0x08077000,0x08078000)`。因此不能將一般 4 KB 擦除等同於這條候選快速擦除路徑，也不能只憑 256-byte 對齊推斷實際硬體擦除影響範圍。實機位址映射、擦除粒度、內容保存及寫入成功仍未驗證。[靜態交叉檢查](check-erase-page-reference.py)只讀本機既有參考來源與重建程式，不執行目標。

## 112／133-byte copy 與固定 256-byte CPU 搬移

六個 writer 均配置 272-byte frame，saved RA 位於 SP+268，先透過 table `0x4004C` 將自己的 record 複製至 own SP，再呼叫 `0x9C0A`。前輪已核對其 program leaf 固定讀取 source 的 256 bytes；這依賴 callee 契約、有效記憶體、無 fault 及 polling 正常結束等條件，仍不證明物理 Flash commit。

四個 256-byte records 的 copy 數值範圍覆蓋 CPU 搬移來源，但不代表來源內容已驗證。112-byte writer 留下額外 **144 bytes**、133-byte writer 留下額外 **123 bytes**：在 writer 內沒有相應的直接 fill／copy，初始化來源仍未知。這些範圍在自身 frame 內且避開 saved RA；沒有觀測到 stack 內容或資料洩漏。**不得自行補零、假設舊值、縮短 Flash 搬移或宣稱整頁已初始化。**

## C/C++ 需求合約與重跑

[requirements-v1.h](requirements-v1.h) 保存與原指令獨立核對的數值；[layout-contract-v1.c](layout-contract-v1.c) 以 C11／C++17 assertions 檢查 page alignment、record/count、RAM nonoverlap／gap、reset-zero 容納關係、source／saved-RA 範圍及兩個額外 source extents。實際編譯物件完全相同，**沒有 allocated bytes、provider、import、relocation 或 executable entry**；不執行物件。

[證據](evidence-v1.json) · [驗證收據](verification-v1.json) · [摘要](summary.json)

```sh
python experiments/tsl9-NVM-record-layout/verify-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

需固定的本機 BIN、前輪 native artifacts 與 Windows NDK LLVM；不下載依賴。若尚未建立新試驗，可加 `--build-trial <全新名稱>` 編譯數值合約；其他平台未驗證。

APP 仍為 159 C/H、95.54% 位元組覆蓋率（不是功能完成率）；SDK 維持 20,490 CODE＋256 DATA、10 個具名依賴。4-byte 啟動來源缺口及實體 ROM／RAM／ISA／IRQ／NVM／Flash／OTA 相容性仍開放。沒有目標／HOST model／ISA／硬體執行；**尚未成功重建可用替代韌體**。後續功能候選為合法 NVM backup 的離線範圍／marker 相容性報告，尚未實作；不自動遷移或寫入硬體。
