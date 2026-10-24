# LLE IRQ原生編譯與連結實驗

[English](readme.en.md) · [分析結果](../../analysis/lle-irq-2026-10-24/README.md)

[lle_irq.v1.c](src/lle_irq.v1.c)原樣整理至 [src/native/irq/lle_irq.c](../../src/native/irq/lle_irq.c)。C負責live GP地址與volatile callback讀取，原始frame／register／JALR／MRET使用明示架構port；沒有宣稱一般C IRQ ABI。

[build-v1.py](build-v1.py)以 [spec-v1.json](spec-v1.json)固定的Windows LLVM配方實際編譯C11／C++17，再檢查134B／64指令、三個60/10/64B定義、零UND／RELA及所有配置bytes。兩個尾端零bytes不編入code。

[integrate-v1.py](integrate-v1.py)以 [joined-v1.ld](joined-v1.ld)接入真實父元件。所有153筆typed引用及local/global owner/value逐一驗證；向量64的size0 alias指向真正60B入口，完整134B包裝層仍保留。

固定工具與完整本機產物俱在時，可唯讀重播：

~~~sh
python3 experiments/tsl9-lle-irq/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lle-irq/build/trial-v1
python3 experiments/tsl9-lle-irq/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-lle-irq/build/component-v1
~~~

LLVM_BIN由執行者設定；Windows可使用已安裝的python。fresh build僅接受新輸出目錄。公開收據不能代替缺少的物件，也不代表已跨機重播。

[父清單推導](parent-manifest-v1.py)還原精確80檔原始bytes；本輪只新增一個來源與native unit。[integration-v1.json](integration-v1.json)固定實際來源、工具與收據。新curation為108組／216物件，加上獨立資料2組／4物件，共110／220；前106組及637筆產物保持一致。舊父元件的全域manifest已擴充，所以以精確extension及其餘所有原輸入／產物核對，不宣稱舊whole-manifest replay仍直接通過。

原callback值、IRQ／ROM／硬體與最終原位址／OTA相容性仍未證，沒有執行韌體或產生BIN。
