# 完整原始映像的 C/C++ 建置保真

本階段用原始位元組補齊先前尚未納入儲存體的95B，C11／C++17的編譯、連結與objcopy產物均一致。離線比對檔 `NOT-FLASH-VALIDATED-original-layout.bin` 為76800B，與原下載ID2966 V4.1.60候選檔逐byte相同，SHA256為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。這證明原映像位元組可由本C/C++工程重現，沒有證明原C原始碼完整恢復、功能已修改、實體硬體／resident身分、啟動／IRQ或原藍牙OTA相容。

## 95B的明示儲存用途

原681個配置覆蓋76705B。剩餘10段：`8004..8038`52B、`81CA..81DE`20B、`8446..8448`2B、`8496..8498`2B、`851E..8520`2B、`18630..18638`8B、`19CA6..19CA8`2B、`19D66..19D68`2B、`19DD2..19DD4`2B、`19DF9..19DFC`3B。

52B是12個可解碼ADDI x0,x0,0及一個EBREAK；20B為可解碼且含RET的片段；8B是四個C.J自迴圈；其餘15B全零。沒有已知入口不證明它們是padding或不可執行，零值也不能自動當作NOP。完整file-fidelity用途可以保留這些原始bytes，同時保留其執行語義未知。

`src/image_only_native.c/h`只新增10個private const uint8陣列，alignment1。metadata為`kind=opaque-image`；ELF flags2只表示本工程使用的source-image carrier，不宣稱原始code／data分類、函式／物件邊界或硬體存取權限。private OBJECT size僅為實際carrier長度。沒有新增canonical符號、code provider、R32、ABS stub、跨版本內容或來源外補值，沒有閉合任何runtime義務。

## 原生實物與輸出驗證

正式W收據：`build/image-fidelity-999d8125159a4d80bd6df9153f267002/verification.json`，SHA256 `2e6585594c1b02de058e2fbb5838f591a5915efed7bc461b9083e99a2e97b8bd`。

- 舊完整681 native gate先fresh重建；全部繼承來源保持。新整合為691個非空allocated sections、8280筆RELA、唯一原resident UND。
- 新unit只有10個PROGBITS陣列／95B，無指令provider、UND或RELA。所有舊section metadata／bytes、raw symbol出現次數、完整raw RELA的site／type／S-role／signed addend／multiplicity保持；原17word表及四個固定原VA records保持。
- 唯一metadata省略為新生成的10個未被任何RELA引用的匿名LOCAL SECTION，以及精確的新非allocated `.comment` mapping marker。按實際SYMTAB與RELA.sh_link/index核零引用，保留舊metadata，不泛化忽略LOCAL／SECTION／ABS。
- C/C++ merged object均為 `646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97`；numeric witness均為 `66fbf4cf1d9731f5fcd4f71c66ec1c67fc4fd2487f710125ed6488cbde2e8420`。
- 每個原VA及byte都由實際PROGBITS承載，聯集恰為`[8000,1AC00)`，沒有gap、overlap或把linker padding算成storage。source coverage為76800B；未納入、LOAD padding mismatch及未覆蓋均為0。
- 每個PT_LOAD的PADDR／LMA必須等於VMA，非零filesz的完整範圍必須在原image內。所有file-backed LOAD bytes與source carriers、原candidate及實際objcopy輸出完全相同；RAM仍為NOBITS且沒有匯入flat BIN，nonALLOC metadata／reference ROM亦未匯入。沒有使用`--gap-fill`；獨立tiny ELF證明objcopy本來會補洞，因此本gate要求實際source carriers完全覆蓋，不能僅靠最後hash。
- 每語言8個merged ELF反例及4個flat BIN反例被拒，涵蓋原byte／size／NOBITS／假的ROM ABS provider／舊code／RELA addend／缺RELA／SECTION visibility，以及改byte／截斷／附加／錯image base。獨立producer另有兩語各14個實物反例。

## 尚未閉合的實機條件

嚴格連結仍因 `__tsl9v4160_rom_entry` 缺少實作而失敗，沒有strict executable。numeric witness只把該原始地址義務寫為40000；離線BIN也未提供resident bytes。原檔與原機目前內容、實際MCU／ISA／ROM、RAM／stack／IRQ、Flash／BOOT及OTA接受條件仍未證明。十項callback與十二項data runtime契約未閉合；已知局部潛在讀域仍有1144B在候選來源之外，完整檔案儲存不代表讀域完整或無fault。

全程沒有原／重建RV32執行或ISA模擬、網路、硬體I/O、刷寫或發布。`source_image_BIN_created=true`只表示產生離線檔案，`flashable_BIN_proved=false`、`native_runtime_ready=false`、`ota_verified=false`、`goal_complete=false`。

```powershell
python -X utf8 -B experiments/tsl9-v4160-startup/verify-image-fidelity.py --current-receipt <實際681收據絕對路徑> --proof-root <本輪proof資料夾絕對路徑>
```

獨立審查位於目的地`analysis/v4160-image-fidelity-2026-10-21/image-review/`。目的地fresh重建與讀回是否完成須另核該輪`destination-verification.json`及W的postdelivery-readback；不能以本W通過代替實機測試或交付完成。
