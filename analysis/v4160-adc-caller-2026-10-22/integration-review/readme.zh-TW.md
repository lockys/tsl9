# ADC caller 注入的獨立靜態審查

[English](readme.en.md) | [繁體中文](readme.zh-TW.md)

本 scope 只讀取已建置的 C/C++ integration 實物，沒有呼叫 integration producer 的 `inspect/replay` 作為判定，也沒有重新連結或產生 BIN。獨立 `struct` ELF32 parser 讀取 header、sections、symbols、RELA、program headers；JAL 立即數與 RA 欄位另外手算，再與既有 typed decoder 及實際 LLVM 完整反組譯交叉核對。上一輪已封存 ABI 的實物收據也重新讀取，確保被連結的110 B 真 C 機器碼就是已審查的 caller-bank 函式。

實際 C/C++ 候選完全相同：78,848 B，SHA256 `ecd2a9fe757117ab8af19211a56c5090dc3a2c777422fcd12ca2fb6298565e55`。基底為既有77,824 B、SHA256 `3be918942c03de99c8a5f3fb7d6eba40ab9af63930020efb7f4cac07cc9a10ee` 的實驗映像；其整個前像除了原 `0x19896` 的四個 caller bytes 都保持一致。該 caller 原本仍與原始 ID2966 的 `JAL→0x1892E` 相同。

assembler 的實際 `call_site.o` 含唯一 `R_RISCV_JAL`（type17）relocation，引用真正尚未定義的 `tsl9_adc_config_1892e` 符號；原生 ET_REL 則真正定義此 FUNC，沒有數字 provider。最終四 byte JAL 跳到 `0x1B000`，位移 `0x176A`，仍令 RA=`0x1989A`。`.s` 的 norelax/norvc、symbolic JAL、`.ld` 的兩個 RX owners 與實際 assembler/linker 參數、工具 hash、成功 log、來源 pin 都另外核對。

linked ELF 只有 `.caller`（`0x19896`、4 B）及 `.adc`（`0x1B000`、110 B）兩個可配置執行 section，各有恰好相同檔案 offset、起始位址、file/memory size 的 RX LOAD。沒有執行跨度的 hole、header、page padding 或 allocated NOBITS，UND0／RELA0／ABS0。容器檔案中非 LOAD 的排版空間不會被拿來製作 runtime page。linked ELF 唯一 FUNC 是真 C110；原物件的四個其他真實全域函式在 GC 後確實消失，而原物件的五個函式仍有前輪審查證據。

基底 `0x8000+77824=0x1B000`，所以只追加一頁1024 B：實際110 B C 機器碼加914 B 明示 FF 尾端資料。逐 byte 核對原前像、caller、C payload 與頁尾，未修改原基底檔。raw BIN 不編碼執行權限，不能把 ELF 的 RX 邊界當成實際硬體存取保護。

每份實物七個 in-memory 反例均拒絕：caller RA、caller target、section size、LOAD 隱藏 memory hole、舊前像、C payload、FF 尾端。沒有把反例寫成新 BIN，也沒有 CPU／MMIO／ISA／ESIL 執行。

候選繼承舊基底的 OTA C568、原始 carrier 與 `0x40000` ROM 位址 witness 限制。新 ELF 沒有 UND／ABS，不代表整個 raw 映像的 ROM provider 已實作；這次只證明新 ADC caller 注入，不是完整 whole-image provenance 或全原始碼重建。caller 正常投影仍依賴有效私有144 B stack、無 alias／非同步干擾、私有 frame 殘值不被觀察及原 polling 正常返回等前提。原 callee 全 ABI、fault／IRQ、Flash/NV ownership、實體 ROM／BOOT／chip、BLE OTA 接受與失敗恢復全部未證實，候選保持 **NOT-FLASH-VALIDATED**。

`check.py --project-root ROOT` 只驗證封存來源與歷史摘要。實際審查使用 `check.py --project-root ROOT --integration-receipt BUILDER/c/verification.json --receipt NEW.json`；`--replay NEW.json` 重新只讀核對全部實物。收據必須全新，支援 W 的 `apk-analysis/tsl9-*` 與 D/P 的 `analysis/*`。回傳 `linked=false`、`BIN_generated=false` 表示這個 reviewer 沒有執行建置；另有 `actual_linked_ELF_read=true` 與 `candidate_BIN_read=true` 明示讀到的既有實物。

本輪沒有新 HOST 矩陣、硬體、網路或再次嘗試 Git Bash；sh runtime 未驗證。新文字 LF、單 EOF，default README 與繁體中文相同，英文另檔。
