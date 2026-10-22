# IRQ 來源整合映像：獨立審查

使用最終凍結 runner，重新以 C11、C++17 編譯並唯讀重播實際產物，兩語均通過。兩者輸出相同的76,800B **NOT-FLASH-VALIDATED** 候選，SHA256 `47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c`。相對固定 ID2966 原檔，只有 `9A44..9A4B` 八個 byte 改變，對應已明列的 prologue 暫存器儲存順序置換。

這是五個函式、合計264B的局部可讀 C 替換：9A42主函式144B，以及19124、19142、19160、1917E各30B。其餘686個原始 storage sections 仍保留原始指令／資料載體。沒有宣稱完整可讀原始碼、實作新增產品功能、逐點／非同步等價、提供實體 ROM，或已證明硬體、啟動及 OTA 相容性。

## 實際證據與來源審查

[review.json](review.json) 綁定最終 runner、可攜 model wrapper、manifest／layout 與實際收據副本。runner SHA256 為 `b26410ae9a0d9dece3e5404fb311407dd7c3022a08a7d2fb8c8df7834496c854`。`prepare_manifest.py` 是歷史來源的一次性擷取；新的正式驗證使用已固定的 manifest 與 layout，不需要舊 build 目錄。

來源過濾只移除五個白名單 quoted-assembly 區塊，各一次，直到精確 `.size`。重播會逐 byte 重算兩份過濾來源的剩餘內容。強制包含的 adapter 在實際所屬編譯單元指定原 section，建立真正 global FUNC alias；C++ 也維持 C linkage。主函式與 helpers 分別沿用已封存的原生編譯 profile，主函式允許實際 callframe，helpers 保持較窄的暫存器限制；LLVM IR 與選定函式 code hash 綁定真正輸出。沒有執行原始或重建 RV32 程式。

每種語言有34個保留 carrier 編譯單元＋2個 typed 單元、36份實際 dependency 檔、71個已固定的原始非系統來源／header＋4個生成輸入、44筆精確 clang／lld／objcopy 命令與144項產物指紋。`-MMD` 不納入編譯器系統 header，因此此處是應用程式 dependency closure，不是整套 sysroot 的完整雜湊清單。來源、proof members、runner 與指定工具檔案亦有前後一致性核對。已實際執行 Python model 入口；shell 入口只作檢閱，沒有在此環境執行。

檢查全部691個原 allocated section 的角色與原 VA。partial object 保留8270筆外部 RELA 的完整 symbol owner／value／type／visibility、signed addend、site 與重複筆數；新主函式保有六筆 typed helper JAL，只解除四筆精確識別的舊 helper branch relocation，總計8276筆 RELA。53個 canonical labels 均維持 section-relative，五個原 global FUNC alias 與八筆靜態外部 entry 引用保存。metadata gate 保留完整舊 ABS mapping 多重集，只增加兩項實際量得的新項目；private-label 例外只准四個完整角色，沒有 prefix wildcard。未知的 computed／interior entry 仍未排除。

嚴格 final link 確實因唯一未定義的 `__tsl9v4160_rom_entry` 失敗，沒有 strict ELF。另一份 script 僅給數值40000，產生 **ADDRESS-WITNESS-ONLY.elf**，不提供 ROM bytes 或 provider。匯出的76,800B全部有真正 PROGBITS section storage 與對應 file-backed LOAD bytes；35160B NOBITS RAM 不輸出。這證明的是檔案 storage 表示，不是完整 PT_LOAD zero-fill 執行語義或實體記憶體行為。

每種語言15個實際變異 ELF／RELA／image 均被拒絕且已重播，涵蓋保留／選定 byte、alias section／type、relative label、relocation addend／筆數、RAM kind、額外 allocated storage、linked VA、LOAD LMA、範圍外／還原的 image byte，以及截短／附加 image。收據保存原因與指紋。本審查沒有複製原 APK／minified JS、憑證或裝置識別資料。

## 靜態加總觀察

[checksum-note.json](checksum-note.json) 記錄有限的算術結果：八個改動都落在 raw plaintext 第6個1024B block（`9800..9BFF`），且 byte 多重集相同。前後 data sum16 都是28349；若加相同的 index bytes `00 06`，則都是28355。APK `ready` 原始碼會連同兩個 index bytes 加總整頁。因此，**僅在這些明文 bytes 確實位於同一個傳輸頁、且 index 不變的條件下**，該頁加總才維持不變；沒有推定 API 編碼或真正傳輸頁映射。

保存的 ID2966 runtime-side W 指令檢查1026B、使用1024 data bytes，數值目的地算式為 `(0x20000+4+page)<<10`，即 `08001000+page*1024`，不同於 runtime image base8000。以上不證明 BOOT／runtime 更新模式相容、簽章／真實性、完整映像接受、Flash 成功或安全 OTA；沒有執行 JS 或目標指令。

## 唯讀重播與重新編譯

```sh
python3 check-review.py --project-root /absolute/project --firmware /absolute/ID2966.bin
python3 check-review.py --project-root /absolute/project --artifact-root /original/archived/final-build
python3 /absolute/project/experiments/tsl9-v4160-irq-image-integration/verify.py \
  --project-root /absolute/project --tool-dir /local/llvm/bin \
  --firmware /absolute/ID2966.bin --language both --build-root /new/output/directory
```

預設 review replay 檢查封存收據 JSON、目前 source／proof 與以原檔推得的 image 算術，不編譯、不產生 image。若 checksum 引用的 APK／CFG 檔案在本機存在，會核對雜湊並回報可用性；私有來源不存在時，保留其來源指紋，不為修補連結而複製內容。指定 `--artifact-root` 會再唯讀重播 archive 中 c／cpp 的全部產物與30個變異；歷史收據保存真實絕對命令與工具路徑，需要保留當時 layout。重新編譯則接受明確 project、LLVM、firmware 與只能新建的輸出路徑，沒有宣稱歷史收據可以直接搬移路徑。

選定收據副本保存在排除的 `build/` 以外；原 objects／ELFs／BINs／logs／dependency 檔／mutants 僅留本機工作 archive。發佈樹的唯讀預檢確認73個 manifest source／header 路徑全已存在且雜湊相同，沒有寫入發佈目錄。本審查只修改自己新 scope，沒有修改實作、舊 seal 或交付專案。

[English](readme.en.md)
