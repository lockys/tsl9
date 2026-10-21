# 加入明確 ABI 排程後的整體映像獨立審查

[English](readme.en.md)

本輪實際讀取最終 C11、C++17 的編譯物件、IR、排程前後物件、連結 ELF、LOAD 與 BIN。兩個 **76,800-byte BIN 都逐 byte 等於原始 ID2966**，SHA-256：

`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`

這是 **C/C++ 編譯輸出，加上明確的 ABI 儲存順序排程**。不是編譯器單獨輸出該儲存順序，也不是已把整份韌體重寫成可讀 C/C++。只有 11 個函式、526 bytes 使用可讀重建來源，其餘 680 個配置仍是原始指令／資料載體。沒有執行目標 RISC-V、模擬器、硬體或網路操作，沒有新增使用者功能已實作的宣稱。

## 實際產生鏈

最終每種語言都重新編譯 42 個 TU：34 個保留載體 TU 與 8 個提供 11 個函式的可讀來源 TU。完整鏈共有 57 個明確命令：56 個 LLVM 命令，以及一次 Python `-B` 排程命令。

```text
42 個來源 TU → raw-carriers.o + typed-providers.o
             → compiler-integrated.o
             → schedule.py → source-integrated.o
             → 嚴格連結失敗／數值 ROM 見證連結
             → objcopy → 實際 BIN
```

本輪編譯／排程／連結／匯出命令沒有把原始 BIN 當作產生輸入。原始 BIN 與原生元件 bytes 用於驗證；保留的舊載體來源本來就含原始指令／資料，並未將其宣稱為新的高階來源重建。八個 adapter 只加入型別、區段與真實 FUNC 別名，沒有從驗證 ledger 輸出 opcode 或把原始 BIN 複製成結果。

實際 `compiler-integrated.o` SHA 為 `63720dca234286d4b2bd012855606c0ca6c01a9effefb3066d1d8889f2657826`；排程後 `source-integrated.o` 為 `4e86cebc1119d30a726386cc520d73c5384920bb74bd97dbbc5dfa505c6bfbf2`。C 與 C++ 兩條鏈的這兩個物件各自相同。

## 14-byte 排程的來源及限制

已審查的工具／政策為 `dc680558…876535d`／`2af7789f…0a694d`。工具只複製新物件已存在的 C.SWSP 半字；沒有合成 opcode、加入填充或使用原始 BIN 產生指令。

| 函式 | 編譯器原有儲存順序 | 排程後順序 |
| --- | --- | --- |
| IRQ `9A42` | RA→SP+12、S0→SP+8、S1→SP+4、S2→SP+0 | S2→SP+0、RA→SP+12、S0→SP+8、S1→SP+4 |
| Flash quarter `9C0A` | RA→SP+28、S0→SP+24、S1→SP+20 | S0→SP+24、S1→SP+20、RA→SP+28 |

獨立檢查器從實際 pre-object 的既有半字重建預期排列，再比較完整 post-object。結果只有 14 個檔案 bytes 改變；長度、全部 ELF 區段 metadata、符號與重定位完全不變，其他函式內容也不變。這並非僅接受排程收據的布林宣告。

工具本身依 ELF 形狀無法認證「新編譯的 C/C++」來源。因此本輪另外核對來源雜湊、42 個實際物件、50 個 Clang 編譯／IR 命令的語言／標準／目標，以及 pre-object 的來源元件 bytes、合併輸入、當前工具與政策、排程命令、post-object 和最終連結輸入。單獨看到正確的 prologue 或歷史排程收據，不足以聲稱完成這條來源鏈。

排程工具拒絕既有符號／記錄重定位對儲存區間的錨定；這不等於證明任意 ELF 沒有已解析直接分支或計算式內部入口。已知函式與呼叫前緣的 ABI 審查由另一個封存提供；計算式／編碼式／ROM 參照不存在仍未證明。舊 standalone 排程測試使用歷史編譯物件，不能算本輪 42 個新編譯 TU；本輪實際 pre/post 鏈另行保留並驗證。

## 獨立驗證的範圍

- 全部 691 個原配置、680 個保留配置的部分物件內容、11 個可讀函式的實際 pre/post bytes，及其真實區段所屬 FUNC 別名。
- 原有 8259 筆外部範圍重定位的角色、型態、有號 addend 與重複次數；新函式 11 筆 JAL，合計 8270。20 筆已知入口參照與 53 個相對區段綁定維持原契約。
- 四個 raw TU 只移除指定 11 個函式；實際 34 個載體物件都沒有遺留這些 raw fallback。
- 實際 42 條 `.d` 規則逐一綁定自己的 `-MT`、主來源與 adapter；合計觀察 72 個既有專案檔與 12 個產生檔，另綁定 10 個排程來源／政策／說明檔。`-MMD` 不包括編譯器系統標頭，沒有宣稱完整系統標頭閉包。
- 實際 15 個 PT_LOAD 的檔案資料、記憶體範圍與每 byte 權限，全部與 691 個已連結區段及 BIN 相符；RAM 保持 `0x20004000`、35160 bytes、NOBITS。
- 六個 Flash IR 的 volatile32 與暫存器／address primitive 來源關係，及製作者的 IRQ IR／完整靜態契約重播。

最終兩種語言各讀回 201 個實際成品／紀錄／依賴檔，並唯讀重播製作者 23 個 ELF／RELA／映像控制、3 個依賴控制與 4 個排程收據控制。新增獨立控制只有兩個實際命令紀錄 JSON：把 C 收據誤標為 C++、或讓 typed IR 的標準與語言不符，均被來源語言檢查拒絕。它們沒有重新啟動編譯器或目標，也不是原生／主機語義 mutant。

前輪已封存的原始指令、原生元件、HOST 行為與負向矩陣按精確身分重用；本輪沒有盲目重跑舊主機 mutant 矩陣。新增證據是兩種語言的整體來源／排程／成品鏈與明確的新來源紀錄控制。

## 可攜使用方式

預設只驗證當前來源、封存與預期 bytes，**不宣稱存在或重播實際建置封存**：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin
```

對新建置的完整實際鏈進行驗證：

```sh
python3 -B source-review/check-review.py --project-root /path/to/project --firmware /path/to/original-ID2966.bin --receipt /path/to/new-build/c/verification.json
```

`check-review.sh` 使用 `PYTHON` 或 `python3`；Windows 可直接使用 Python。發佈只保留來源、收據 metadata 與報告，不包含本機完整 build archives。歷史收據中的路徑不表示那些檔案在其他電腦仍存在；在新目錄請傳入該目錄真正的新收據。可攜模式不需要 W-only 的舊物件或 frame ABI 測試封存，會明確輸出 `original_baseline_archives_replayed: false`。

## 仍未證明

嚴格連結仍因缺少 `__tsl9v4160_rom_entry` 而失敗。見證腳本只把符號設為 `0x40000`，沒有 ROM 內容或實作。BIN 相同不代表已驗證 ROM 合約、實體啟動、晶片／Flash 相容性、故障／非同步行為、已安裝 BOOT 或 OTA 接受條件；這些欄位仍為 false／unknown。也沒有將保留載體誤稱為完整的可讀 C/C++ 原始碼還原。
