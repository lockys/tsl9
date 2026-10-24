# 既有CAN RX0 C/C++單位的連結

[English](readme.en.md) · [分析結果](../../analysis/can-rx0-irq-bind-2026-10-24/README.md)

來源為 [ring_irq_adapter.c](../../src/native/irq/ring_irq_adapter.c)、[irq_provider.c](../../src/native/receive/irq_provider.c)、[ring_insert.c](../../src/native/receive/ring_insert.c)，沒有修改原C/H或manifest。

[integrate-v1.py](integrate-v1.py)重播當前來源及父元件，讀取三個真實C11／C++17物件，逐一核對16個region及9筆original control relocations。原opcode／register／condition bits與目標均須吻合；純資料編碼回原位址後，完整308B必須與原廠相同。[contract-v1.json](contract-v1.json)固定物件、來源、工具、原碼與範圍。

[joined-v1.ld](joined-v1.ld)依原順序保留各span的fall-through／cold block，再綁定向量36與真實12C24入口。alias是size0的section label，真實入口region為14B，完整adapter共52B，不是空handler。

使用固定工具鏈與完整本機產物，可唯讀重播：

~~~sh
python3 experiments/tsl9-can-rx0-irq-bind/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-can-rx0-irq-bind/build/component-v1
~~~

LLVM_BIN由執行者指定；Windows可用已安裝的python。fresh build只接受新輸出目錄。公開收據不替代缺少的編譯物件，也不證明跨機重播。

本輪僅新增partial link；當前80檔／53個code單位＋1個資料單位的108組來源比對／216物件仍經完整父證據核對。所有153筆typed引用及local/global owner/value皆驗證；這不證明所有RAM指標或IRQ／resident ABI。

原12BD2 AUIPC與4004C間接呼叫均保留；最終原位址配置、RAM／ROM／IRQ與BLE OTA仍未證明。沒有執行韌體或產生可刷BIN。
