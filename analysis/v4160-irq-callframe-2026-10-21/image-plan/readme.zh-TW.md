# 僅建立新成果的來源整合計畫

目前 C/C++ callframe probe 均為 main144＋四個 helper 各30，符合原始範圍；與原始 BIN 僅 **`0x9A44..0x9A4C` 八 bytes** 不同，為四個完整二-byte prologue store 順序排列。最終 frame slot 相同，offset10 起完全相同。這是元件結果，尚非新整體映像驗證。本審查沒有產生 object、ELF 或 BIN。

基準為 `image-fidelity-999d8125159a4d80bd6df9153f267002/c/source-image-merged.o`，SHA `646dbe43...`；上一層實際 `original-image-layout.ld` 為126450 bytes、SHA `651a8f14...`，具有691個精確位址／大小 assertion。小型 ROM script 僅是數字 witness。`exports/v4160-image-fidelity-stage.json` 綁定基準 receipt。原 carrier 有691 allocations、8280 RELA，唯一真 UND 為 `__tsl9v4160_rom_entry`。

需替換的五段為 `.text.tsl9v4160.init_9a42`（`0x9A42`／144）、`.text.tsl9v4160.frontier_19124/19142/19160/1917e`（對應原址／各30）。必須保留真實 section-backed FUNC aliases `__tsl9v4160_call_9a42/19124/19142/19160/1917e`，offset0、原始大小。ledger 列出新 C 名稱、19個原 symbol records、94個來源指令 labels、10個原有 owned RELA、8個外部 incoming RELA。外部參照都是入口 type17 JAL、addend0；四個 helper 的 offset14 私有 labels 只被各自原 type44 branch RELA 使用。尚未排除計算式間接內部入口，尤其變更後的 prologue。

## 最小來源重建，不重跑歷史巢狀測試

ledger 的 `transitive_source_units` 是從13個實際 receipt lineage 正規化取得的 **34個 TU 精確清單與雜湊**。不能只 glob `*_native.c`，還有 `src/startup.c`、`src/clock.c`。來源宣告掃描確認正好691個唯一 allocation 名稱，符合基準全部 section：645個 `.section`、1個 `.pushsection`、35個直接 C section attributes、10個 `ORIGINAL_RO` 實例。實際690個 file-backed extents 無缺口／重疊覆蓋 `0x8000..0x1AC00` 的76800 bytes，另有35160-byte NOBITS RAM。

舊 carrier 共用 flags 為 `--target=riscv32-unknown-elf -march=rv32imac -mabi=ilp32 -ffreestanding -fno-builtin -fno-stack-protector -Wall -Wextra -Werror`，明確 C11／C++17 再 `-c`。兩個 readable TU 仍使用其獨立驗證的較嚴格 profile；不可從本計畫推論新最佳化設定。

34個 TU 尚不足以提供全部 canonical address labels。七份既有 section-relative scripts 提供 **53個相異 global NOTYPE／size0 bindings**，已逐項核對實際 carrier 的 owner／offset／type／visibility，路徑、hash、expression、行號均在 `section_relative_bindings`。包含 static vector-ram-views(7)、callback-address-bindings(10)、retained-data-addresses(12)，及 lineage 內 data-anchor actual-RAM-views(2)、table-extension actual-RAM-views(5)、core-extension actual-RAM-views(16)、dependencies real-RAM-view(1)。可合成單一零 VMA partial-link script：每段 **KEEP 前** 使用 `. + offset`；已證明 RAM labels 用 `__tsl9v4160_ram + offset`，不得改成數字 ABS。

1. 建立新的 sibling integration 目錄；固定 carrier／layout／receipt、34個來源與 headers、新 typed sources。所有歷史來源與證據維持不變。
2. 僅複製 initialization_native.c、frontier_native.c，以精確 section allowlist 移除1＋4個原 assembly blocks，保留其他文字與 option wrappers。其餘32個原始 TU 不改。filtered carrier 應正好保留686 allocations，不含五段 storage／providers。
3. 每種語言僅編譯一次新兩個 typed TU。可用新 forced-include adapter 在既有 function declarations 指定原 section 名稱；原 provider aliases 必須在**擁有函式的同一 TU** 建立，並實查 section-relative FUNC、offset0、size144／30。可額外保留 public C 名稱，但不能使用 ABS、假 size0 provider、wrapper 或增加 storage。跨 TU `.set` 可能消失或繼承錯誤型別，須查實際 symbol records。
4. `ld.lld -r --no-relax` 合併各 unit，加上合成53-label script。維持691個原 section、大小／alignment／type。四個舊私有 branch labels 可連同已無用途的四個 RELA 明確解除：新 helpers bytes 相同、分支已在內部解析。五個 global aliases 及所有仍被參照角色必須保留。SECTION／mapping markers（`$d`／`$x`、編號、檔名 metadata）差異應逐項限定，不能放行任意 symbol 改變。
5. 證明686段 storage hashes 相同、RAM 仍 NOBITS；以 multiset 核對全部 **8270個非替換範圍 owned RELA**（owner／site／type／symbol-role／signed addend）。八個 incoming alias 仍連到原入口。新 main 只增加原offset1C/28/32/3C/46/50的六個 type17 JAL；新 helpers 無 RELA，解除四個原 type44。因此新總數應為 **8276，不是8280**，不能為滿足舊數量捏造紀錄。
6. partial object 仍只能有 ROM UND；使用原691配置做 strict link 應因缺少 resident 失敗。另行 numeric witness 可設 ROM=`0x40000`，不代表提供 ROM 實作。檢查691 placements、690個原始來源 file sections、LOAD VMA/LMA及排除 RAM。
7. 上述通過後，已授權的 integrator 才輸出**新命名、未驗證燒錄**的離線映像。逐 byte 比對76800 bytes，必須僅有八個已允許差異、helpers及其他 bytes 相同。不可 patch／覆寫舊 BIN，也不可用原 bytes 補救失敗 section。

原 `verify-image-fidelity.py` 的 allocations、完整 layout、merge、strict／numeric link 與 image gate 是具體既有 API，但它要求全部等同原始 bytes，應保持封存，另寫限定差異 gate。原 producer generators 位於 initialization-review/generate-native.py 與 frontier/native/generate-frontier.py；實際使用其 staged source copies。ledger 固定 generator／staging 路徑雜湊。可用既有驗證 artifacts／source pins，無須重跑巢狀歷史681-stage pipeline。

本審查沒有實際編譯34-unit rebuild、重建53 bindings或連結整體候選；來源宣告／alias inventory 支持此計畫，但仍須實跑所有 gate。八-byte 差異及一般 callframe 一致，不證明變更保存順序期間的 stack／中斷時序、ROM、硬體、OTA 或可燒錄。
