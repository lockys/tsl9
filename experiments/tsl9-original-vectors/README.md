# 原廠向量指標資料C/C++實驗

[English](readme.en.md) · [分析結果](../../analysis/original-vectors-2026-10-24/README.md)

[boot_vectors.v1.c](src/boot_vectors.v1.c)原樣整理至 [src/native/startup/boot_vectors.c](../../src/native/startup/boot_vectors.c)。[spec-v1.json](spec-v1.json)固定全部82個word與編譯配方；地址宣告僅供保存pointer，不證明可用一般C ABI呼叫。

[build-v1.py](build-v1.py)編譯並檢查真正的指標資料物件；origin／curated之間除FILE身分外，完整section與symbol投影必須一致。[integrate-v1.py](integrate-v1.py)以 [joined-v1.ld](joined-v1.ld)接入前一輪真實啟動元件，核對144筆引用的完整ownership。未增加handler替身、ABS provider、RAM配置或硬體操作。

若已保留本機完整產物與固定工具鏈，可唯讀重播：

~~~sh
python3 experiments/tsl9-original-vectors/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-vectors/build/data-v1
python3 experiments/tsl9-original-vectors/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-vectors/build/component-v1
~~~

LLVM_BIN由執行者指定；Windows可使用已安裝的python。正式build只接受新的輸出目錄。公開收據不能代替缺少的本機編譯產物，也不證明已跨機重播。

source-manifest內的native_data_units由本實驗獨立驗證，沒有修改舊函式驗證器。一般來源檢查另外使用build/curated-source/original-vectors-20261024-v1/verification.json，仍為53個code單位、106組比對／212物件；本資料單位另有2組／4物件。

[父清單推導](parent-manifest-v1.py)重建前一輪79檔清單的原始bytes。本輪只新增一個C檔與獨立資料單位登記；[integration-v1.json](integration-v1.json)保存實際收據、來源、物件與工具雜湊。前一輪整體manifest已被擴充，因此不宣稱舊全域replay仍可原樣使用；新的檢查驗證精確擴充及其餘所有父產物與輸入。

完整IRQ上下文、原硬體與ROM、main／記憶體及BLE OTA尚未通過；沒有產生可刷BIN。
