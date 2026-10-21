# 整體來源映像獨立契約審查

[English](readme.en.md) · [繁體中文獨立檔](readme.zh-TW.md)

最終 source-integrated-99841... 的 C、C++ 實際 artifacts 均通過獨立讀回。兩份 76800-byte 映像相同，SHA-256 為 47f200dce24be25ac89d57922689da536259935e8615ba8195b10ca192895e1c；與原始 runtime 僅 0x9A44..0x9A4C 八 bytes 不同，為四個二-byte stack stores 的排列。這是新離線映像的檔案／靜態契約證據，尚未證明可燒錄。

## 實際通過範圍

- 新 partial ELF 有精確 691 個 allocation，維持原型別、flags、大小、alignment、entry size 及相對位址；其餘 686 段 storage 不變，RAM 保持 35160-byte NOBITS。
- 全部 8270 個範圍外 RELA 以 owner／site／type／完整 symbol role／signed addend 的 multiset 比對，含八個原 incoming references。新 main 六個 JAL 保留原 offset，helpers 無 RELA；解除四個舊私有 branch RELA 後，總數正確為 8276。
- 所有原 global／weak roles 均保留，只多五個 public C FUNC aliases。53 個 canonical bindings 仍是實際 section-relative NOTYPE／size0；partial object 唯一 UND 仍是 ROM entry。
- 真正 linked ELF 的 691 段皆位於原址，entry=0x8000，所有 LOAD 的 VMA=LMA，690 個來源 file sections 完整覆蓋 76800 bytes。sections／LOAD／輸出映像逐 byte 一致，無 padding 補洞、沒有輸出 RAM 或 ROM bytes。
- 每種語言實際執行 17 個記憶體內 raw ELF／image 變異測試，全部拒絕。包含 ABS alias、錯誤大小、遺失／修改 RELA、額外 allocation、RAM 改 PROGBITS、移動 VA／LMA／ELF entry、越界及「允許範圍內但值錯誤」的 byte。這些不是 compiled source mutants，也未執行 ISA。

## 來源與 metadata 核對

source-provenance.json 獨立核對最終 runner 1929598ffc723937e8cd6bcafbe507fb5ff23f6d9541f00043bdadcb44f3455a、portable manifest、兩份實際 build receipts、每份 144 個 artifacts／logs、44 個實際命令及 36 份 compiler dependency rules。實際 71 個 native sources／headers 與四個生成輸入均有 pin；兩份 filtered carrier 只移除原五個 assembly blocks，其他 bytes 不變，兩份 adapter 只有宣告、section attributes 與同 TU 真 aliases。53-label script 的完整 691 段／KEEP／assertion 與 assignment grammar 另行核對；所有 object 輸入與輸出都在新的 build folder，未使用歷史 carrier object 作為新建輸入。

只接受量測過的 metadata 差異：五個選定函式各自 $d→$x；兩個新增 typed TU 各帶一個 FILE、一個 .comment marker 及一個 attributes-origin ABS $d marker，全部未被 RELA 引用。實際 main.o 的 $d.2、helpers.o 的 $d.5 原屬非配置的 .riscv.attributes，partial link 後轉成 local ABS0；.comment markers 仍屬 .comment。這不是 numeric provider。其他 local／SECTION roles 均保留；四個舊 helper 私有 branch labels 只隨其唯一舊 branch RELA 解除，沒有放寬 global aliases。

最初 ff18322a... runner 在 final binding 前因 relative replay path 修正而改變，審查有偵測並停止 closure；之後使用 1929598f... 真正重新建立 C／C++，沒有將舊 receipts 改綁新程式。正式選定證據是 final-c.json、final-cpp.json 及 source-provenance.json；preliminary-c.json、review-c.json、review-cpp.json 僅保留早期歷史結果。

## 重播與限制

在此專案根目錄，以 Python 執行 artifact checker；不會編譯或產生映像：

~~~sh
python -B apk-analysis/tsl9-v4160-irq-image-integration-2026-10-21/contract-review/review.py --merged /path/source-integrated.o --linked /path/ADDRESS-WITNESS-ONLY.elf --image /path/NOT-FLASH-VALIDATED-irq-callframe.bin --label c --output /path/this-review/replayed-c.json
python -B apk-analysis/tsl9-v4160-irq-image-integration-2026-10-21/contract-review/provenance.py
~~~

checker 需保有此 case 綁定的歷史 baseline ELF、原始 BIN、plan 及 parser；缺少時會停止。生成來源／receipts 的平台路徑不是新機器已完成建置的證據。dependency rules 使用 MMD，排除 system headers；沒有宣稱完整 toolchain 環境的獨立重建。

strict link 實際因唯一缺少 ROM resident 失敗；numeric witness 的 ROM=0x40000 只是數字，不是 ROM 實作。八-byte prologue 儲存順序改變，使原始保存過程中的暫態 stack／非同步 IRQ 等價仍未證明。沒有實體硬體、BLE、CAN、刷寫、OTA 或 target execution。本 reviewer 沒有重複編譯或產生 BIN，也沒有修改舊來源／封存證據。

