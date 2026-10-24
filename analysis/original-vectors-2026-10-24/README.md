# 原廠向量資料與啟動元件

[English](readme.en.md) · [結果](summary.json) · [C/C++來源](../../src/native/startup/boot_vectors.c)

以真正的C函式地址陣列保存原廠8038–8180的328B資料：62個非零地址、20個零值word、61個不同入口。**82個word不是已確認的硬體IRQ數量**；尾端零值一併保留，完整硬體向量表範圍仍未證明。

C11／C++17均產生62筆R_RISCV_32。每個slot、型別、addend與目標逐一核對，純資料重定位驗算後全部328B與原廠相同。沒有以固定整數或假的函式替代未解析入口。

| 真實部分連結 | 結果 |
| --- | --- |
| 程式與資料 | 原572B／212指令＋128B初始化資料保持不變，再加入328B向量資料 |
| 引用 | 144 RELA；55個指標槽連到已重建的真實入口，7槽仍指向6個外部入口 |
| 未解決項目 | 8448、8498、979E、12C24、16FB6、19BD4，以及main9008與resident40000，共8 UND |
| 產物 | C／C++相同；VMA0 ET_REL，不能當作可刷寫BIN |

source-manifest另設native_data_units登記這個純資料單位。舊函式驗證器保持不變：53個code單位的106組比對／212物件通過，前106組結果及637筆產物紀錄全部保持一致；獨立指標資料另有2組來源比對／4物件。合計108組／216物件，來源清單共80個C/H檔。這不代表所有legacy reference都納入原機編譯。

[證據索引](publication-provenance.json)提供3份可攜式原收據，以及1份只代換路徑、可逆核對的資料編譯收據衍生檔；原始收據均保留本機。[六個入口的有界前綴](entry-frontier.json)每個最多64B，可能跨過RET／MRET進入相鄰程式，不能當作完整函式或IRQ相容性證明。

本輪增加了離線向量覆蓋報告能力。原機的啟動／IRQ健康診斷仍只是候選功能，須先證明IRQ上下文、狀態ownership與診斷協定。

原機MCU、ROM、完整IRQ、記憶體、main閉合、最終配置、實際啟動與BLE OTA仍未驗證；未執行目標、HOST模型、ISA模擬、硬體或網路操作，也未產出BIN。commit／push因歷史個資持續暫停。

[實驗與重播方式](../../experiments/tsl9-original-vectors/README.md)。
