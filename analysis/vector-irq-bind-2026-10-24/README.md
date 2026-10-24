# 向量39接入真實IRQ程式

[English](readme.en.md) · [結果](summary.json) · [C/C++來源](../../src/native/irq/irq_flag.c)

選用既有的完整16FB6–17002 C/C++ handler：76B／21指令與原廠完全相同，結尾保留MRET。來源與manifest保持不變。

向量第39槽（原80D4，值16FB6）現在透過section-relative label連到真正的76B函式。alias本身size0，但與完整provider共用實際section／offset；沒有新增空handler或ABS位址替身。

| 真實部分連結 | 結果 |
| --- | --- |
| 程式／資料 | 648B／233原指令＋456B資料；先前572B程式及456B資料保持不變 |
| 符號／引用 | 100個非零架構FUNC區域、1個明示FUNC alias、144 RELA、7 UND |
| 向量 | 56個槽連到真實程式；6個槽仍指向5個外部入口 |
| 驗證 | C11／C++17產物相同；目前108組來源比對／216物件證據仍通過 |

[硬體SDK對照](hardware-sdk-match.json)發現三項一致：本機保存的CH32V20x header中EXTI9_5_IRQn=39、EXTI_BASE=40010400、INTFR位移14，對應原廠向量39與40010414存取。這支持CH32V20x相容EXTI配置的推論，**不等於識別實體晶片或GPIO腳位**；mask寫回的清除語意也尚未以周邊文件／實作驗證。

原碼分別讀取狀態、測試40／80，並把1／2 OR進then-live GP+360 byte。候選新功能是分來源IRQ診斷，但尚未加入counter、額外MMIO或BLE操作。

剩餘入口為8448、8498、979E、12C24、19BD4、main9008及resident40000。MRET本體吻合不證明IRQ暫存器保存、巢狀／fault或原機ROM上下文相容。資料中的82個word也不證明硬體IRQ數量。

本產物是VMA0的ET_REL，76B provider在診斷code offset572，**不是其原16FB6執行位址，也不是可刷BIN**。最終原位址配置、原硬體、記憶體、完整IRQ／main／ROM及BLE OTA仍未驗證。

[三份原收據的索引](publication-provenance.json)逐byte對照本機保留證據，沒有改寫原收據。[實驗與重播](../../experiments/tsl9-vector-irq-bind/README.md)。本輪未執行目標／HOST模型／ISA模擬或硬體／網路操作；commit／push因歷史個資持續暫停。
