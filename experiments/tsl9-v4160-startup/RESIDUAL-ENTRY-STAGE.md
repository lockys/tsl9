# V4.1.60：四個 residual entry 的原生整合

本階段新增原始來源指標所選出的四個條件入口，保留既有平台及 opaque 契約。C 檔使用 inline assembly 保存有證據的指令儲存體；不是高階 C 原始碼還原，也沒有為未知呼叫虛構 C prototype。

| 原始區間（右端不含） | bytes | 來源指標的位置 |
|---|---:|---|
| `10C34..10C36` | 2 | 原檔 `1A67C` 的 LE32 |
| `10C36..10C7A` | 68 | 原檔 `1A674` 的 LE32 |
| `10D2E..10D30` | 2 | 原檔 `1A66C` 的 LE32 |
| `10D30..10D60` | 48 | 原檔 `1A668` 的 LE32 |

合計120B、42指令、4個實體 code sections、4個自有 GLOBAL NOTYPE/size0 anchors。原程式將兩組資料位址交給 nominal resident slot `401B0`；指標的存在及呼叫端資料流是已確認的靜態事實，未知 resident 如何選用、呼叫這些值仍未證明。沒有把兩個12B來源快照當成完整原 C record extent。

`10C36` 比較輸入與三個既有 RAM halfword，匹配後選取12B stride中的 byte並寫入輸入低byte。`10D30` 包含兩個未知間接控制轉移，第一個正常返回後計算餘數1000000；僅憑運算不能命名其實際硬體用途。三個 RET與完整原指令均保留。四組 RAM HI/LOW及五個 direct controls形成13筆新RELA；沒有新增RAM、RO、record、table或canonical provider。

## 實際編譯與檢查

W收據：`build/residual-entry-extension-98daf685c74343d0affb82bac961a05e/verification.json`，SHA256 `69f33a420171620676b9beb9e01bcb68800a998764d820767330f11e2f64f074`。

- 原656 verifier與所有繼承來源未改。新verifier先重新通過完整656基線，再編譯C11/C++17並以真正的relocatable objects整合。
- 實際660個非空allocated sections、8280筆RELA；兩種語言的object SHA256均為 `72aa6c1ea1c081a56a3601052ced8f445a50e05fe79e311292fa7e05db4a354b`。
- 每個舊allocation的type、flags、size、alignment及bytes保留；所有raw symbol occurrence含visibility與multiplicity保留。RELA同時比對semantic Counter及referenced symbol role/signed addend，不能以相同S+A掩蓋契約改動。
- 原17word fixed-address table沿用舊plan檢查，沒有新table或relocation。新程式沒有重複儲存已納入的`11356..11442`。
- 每種語言17個真正ELF byte-mutant均被拒絕，包含同S+A但改寫symbol/addend、舊資料、舊local/global角色、舊負addend與table。這些是有界欄位反例，不宣稱通用ELF validator。
- strict final link仍拒絕原有23個true UND，沒有strict executable。`ADDRESS-WITNESS-ONLY.elf`僅使用數字位址義務核對配置與bytes，不是實作完整的韌體或可刷寫產物。

| actual source/LOAD accounting | 前656基線 | 本660整合 |
|---|---:|---:|
| 已納入原檔bytes | 76300 | 76420 |
| 尚未納入bytes | 500 | 380 |
| gaps中的file-backed LOAD bytes | 414 | 294 |
| 上述LOAD與原檔不同bytes | 309 | 193 |
| gaps中沒有file-backed LOAD的bytes | 86 | 86 |

本輪28個剩餘區間在receipt逐項記錄；零值、FF、可解碼序列均沒有自動視為padding或可達程式。bytes數量不代表功能完成度、原機相容性或release readiness。

## Reference resident 的條件證據

同輪`analysis/v4160-residual-frontier-2026-10-21/rom-gatt-contract`與`rom-storage-callbacks`保存官方V1.31 reference的raw證據，不是原機resident身分證明。

- Reference `40130`消費16B stride attributes並寫入`+10`的u16 handle，callback node保存原record指標，後續讀`+0/+4/+8`。因此可讀性與內容須延續至後續消費；服務新增後callback node失敗也沒有本地rollback。
- Reference `400A4`複製64B config至resident RAM，再由該副本消費callback；6個read及2個write sites使用word count。原`197BE`固定256B wrapper僅在block設定為256B等條件下吻合，不據此證明原機Flash成功或IRQ安全。

完整原硬體SKU、實際resident/ISA、RAM初始化與生命週期、IRQ ABI、Flash/BOOT/OTA相容性仍未閉合。23個canonical UND全部保留。沒有原始或重建RV32執行、ISA模擬、硬體I/O、網路、BIN組裝或刷寫。

重建驗證會建立新的build資料夾，僅編譯/連結/檢查：

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-residual-entry-extension.py --current-receipt <實際656收據絕對路徑> --proof-root <本輪proof資料夾絕對路徑>
```

目的地交付須重新編譯並逐檔讀回；是否完成交付以目的地`destination-verification.json`與W的postdelivery-readback收據為準。
