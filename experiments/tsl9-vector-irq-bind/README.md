# 既有C/C++ IRQ的原生連結

[English](readme.en.md) · [分析結果](../../analysis/vector-irq-bind-2026-10-24/README.md)

[integrate-v1.py](integrate-v1.py)重播當前完整來源及父元件，再讀取既有 [irq_flag.c](../../src/native/irq/irq_flag.c)的真實C11／C++17物件。完整76B必須與原16FB6–17002相同，所有配置、符號與零外部依賴均逐項驗證。

[joined-v1.ld](joined-v1.ld)在unresolved診斷元件內綁定真實provider與section-relative alias。[contract-v1.json](contract-v1.json)固定來源、工具、原廠碼及父產物。所有144筆引用、資料與舊程式prefix必須保持一致，只有對16FB6的真實binding改變。

使用固定工具鏈及保留的完整本機產物，可唯讀重播：

~~~sh
python3 experiments/tsl9-vector-irq-bind/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-vector-irq-bind/build/component-v1
~~~

LLVM_BIN由執行者設定；Windows可用已安裝的python。fresh build只接受新輸出目錄。公開收據不能代替缺少的物件，也不表示已跨機重播。

本輪沒有新增C/H檔、變動manifest或重編新的handler。當前80檔／53個code單位＋1個獨立資料單位的108組來源比對／216物件仍經父檢查核對。這是可追溯的原生部分連結，不是實機、IRQ ABI或燒錄相容性證明。
