# 原機 callback 指標的 section-relative 綁定

本階段補正原生工程的位址解析：十個原始 callback 指標的指令儲存體已存在，這些原始引用只有 PCREL_HI20/addend0 與自己的 LOW12_I，用來形成固定地址。它們沒有 direct CALL/JAL、C prototype 或非零 symbol size。新建置在現存 code section 的精確 offset 定義 GLOBAL/default-visible/NOTYPE/size0 標籤，無新增原檔 bytes、函式、stub、ABS 代用品或跨版本內容。

這是**指標常量的解析**。它不證明 resident 實際呼叫、C ABI、callee clobber、record／指標生命週期或實體硬體相容性。十項 callback runtime 契約仍明列為未知，不能用 ELF UND 數量當作原機執行契約完成數。

| canonical 尾碼 | 原始入口 | 原 section 內 offset | 原取址 HI PC |
|---|---|---:|---|
| `901a` | `901A` | 0 | `909A` |
| `b0d0` | `B0D0` | 0 | `B128` |
| `11442` | `11442` | 236 | `12632` |
| `119c8` | `119C8` | 0 | `12546` |
| `17476` | `17476` | 136 | `1760C` |
| `174ee` | `174EE` | 256 | `17644` |
| `1979a` | `1979A` | 54 | `19A76` |
| `197be` | `197BE` | 0 | `19A80` |
| `197f0` | `197F0` | 50 | `19A92` |
| `1995c` | `1995C` | 414 | `19B26` |

`layout/callback-address-bindings.ld` 在實體 output sections 內建立上述標籤；不是在來源外用絕對數字假造本體。原有 private anchors、程式／資料／RAM storage、其餘符號與所有原取址 addend 保留。這沒有宣稱完整原 C function extent 或任意未知間接入口已被恢復。

## 實際證據與驗證

獨立 callback 證據位於目的地 `analysis/v4160-contract-audit-2026-10-21/callback-obligations/`；原 W seal SHA256 為 `6ab9a215539bbc8730132faa38a8b28e414f33abaa7d9e1497dfcd7ff870e67a`。十個原始 AUIPC／ADDI 的暫存器、immediate、實際目標與 LOW own-HI 逐項從原檔及 actual ELF 核對，entry 必須是已保存的 instruction start 及真 code anchor。

W 正式收據：`build/callback-address-bindings-0b4a6ce2f7784943addbbae92d816c61/verification.json`，SHA256 `4902657856615eb9ce94db4c88e93c8d462441067505c1256e7035dce44f77be`。

- 舊660 verifier與全部繼承來源未改；先 fresh 重編譯 C11／C++17及完整660基線，再用 relocatable link 綁定十個真標籤。
- 十筆 UND→defined 是唯一 raw symbol role 變更；名稱、type、size、visibility、精確內部 offset及出現次數均驗證。其餘完整 raw symbol Counter 保持，不能摺疊同名項。
- 全8280筆 raw RELA只准上述十個 referenced-symbol role轉換；site、type、signed addend、name與multiplicity均保留。全部原 S+A 表達式仍相同，LOW仍指回自己的HI。
- 660個非空 allocated sections的type／flags／size／alignment／bytes保持；原地址配置後每個已納入 byte、舊17word table與全部 LOAD padding均不變。
- 每語言14個真正 ELF byte-mutants被拒絕，包含ABS／FUNC假標籤、內部offset誤設0、同名重複、未規劃的資料provider、LOW缺失，以及相同數值但改用private symbol的RELA。
- C/C++ integrated object均為 `9952f90244819aa224ccbfd2b3de951b62507d4e6557e7eb75be65fe9cab457f`，數值witness均為 `d3408885729609232e33e919277282b3ac3a423079fc74b8954d7b5949a307a4`。

已納入原檔 bytes仍為76420／76800；380B未納入、其中294B為file-backed LOAD間隙、193B與原檔不同、86B沒有file-backed LOAD。上述數字完全未因本次標籤綁定改善，也不是功能完成度。

## 尚未完成的執行契約

嚴格 final link仍精確拒絕13項：12個資料地址及resident `40000`。資料地址為 `19DE0,19DFC,1A078,1A0D8,1A430,1A454,1A478,1A638,1A668,1A674,1AAE8,1AB48`。數值witness只為這13個位址義務提供數字，沒有提供其實作、完整資料域或resident。**沒有strict executable或可燒錄BIN。**

舊階段以23 UND保留 callback 語意未知，是當時明示的保守模型；其收據與來源沒有重寫或失效。本階段將已證的instruction-address解析與未證的runtime契約分開記錄，不把歷史規格重新解讀成原機測試失敗，也不降低硬體／OTA驗收要求。

同輪 index-domain audit掃描24585條已納入原指令，找到三個直接GP-relative byte stores：GP+370寫`(fresh+1)%7`，GP+176兩處寫`(fresh+1)&3`，reset也清零這些位置。GP+176的`A054→A0EA→A1F6→A114→A146`局部路徑避開了`A0FA`遮罩寫入；兩個byte的所有alias、resident及IRQ寫入亦尚未受約束。因此原1AAE8的1024B及1AB48的512B首次讀域仍保留，不能只用正常初始化或測試值縮小它們。

同輪 central-callbacks audit在已保存官方V1.31 reference中追出1A668／1A674兩組三個word的六個消費路徑，各有條件最小讀窗12B且保存原指標；這不是原機resident身分、完整record extent、可變性或生命週期證明。

完整硬體SKU、實際resident／ISA、ROM／RAM／stack／IRQ、Flash／BOOT與原藍牙OTA接受條件仍待證明。十項 callback runtime契約亦未閉合。全程沒有原始或重建RV32執行、模擬、硬體I/O、網路、BIN輸出或刷寫。

重建命令（只編譯／連結／檢查，建立新的build目錄）：

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-callback-address-bindings.py --current-receipt <實際660收據絕對路徑> --proof-root <本輪proof資料夾絕對路徑>
```

目的地交付與fresh build是否完成，須另核`analysis/v4160-contract-audit-2026-10-21/destination-verification.json`及W的postdelivery-readback收據。
