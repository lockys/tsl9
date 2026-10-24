# 原廠LLE中斷包裝層C/C++重建

[English](readme.en.md) · [結果](summary.json) · [來源](../../src/native/irq/lle_irq.c)

已重建8498–851E的完整134B／64指令，C11／C++17皆與原廠bytes完全相同。三個架構region為60B入口、10B callback、64B出口；保留128B frame、29組save/load、GP+384 fresh callback、完整寬度JALR與MRET。原包裝層沒有保存GP，這點也保留。尾端851E–8520的兩個零值bytes另記為資料，沒有假作code。

| 真實部分連結 | 結果 |
| --- | --- |
| 程式／資料 | 1090B／399原指令＋456B資料；父元件956B程式及全部資料保持不變 |
| 架構區域／引用 | 119個非零FUNC區域、3個明示alias、153 RELA、5 UND |
| 向量 | 第64槽接到真實60B入口，完整134B包裝層都在；58個槽連到真實程式 |
| 來源驗證 | 81個C/H、54個code單位＋1個獨立資料單位；110組比對／220物件 |

新的一般來源驗證為108組／216物件，先前106組結果及637筆產物紀錄保持不變；獨立指標資料另有2組／4物件。使用本輪固定Windows LLVM工具鏈，尚未跨機驗證。

[Callback來源線索](callback-origin.json)在199E2起的有效prefix中看到：從字面位址20000008載入，之後存到then-live GP+384。只找到一個直接GP+384 SW編碼候選，但未做完整alias／初始化唯一性分析；8EA8也只列為直接JAL編碼候選，尚未證明包含函式與啟動可達性。

~~~mermaid
flowchart LR
  RAM["word20000008 /value unknown"] --> INIT["199E2 prefix /pointer copy"]
  INIT --> GP["then-live GP+384"]
  GP --> IRQ["8498 LLE wrapper"]
  IRQ --> CB["full-width JALR /provider unknown"]
~~~

與保存SDK的CH32V20x_D8W向量64配置對應，仍是軟體配置候選；不能據此確認實體晶片。真正的callback值／ABI、GP與SP契約、IRQ巢狀／fault及啟動路徑仍未證。

目前VMA0 ET_REL把包裝層放在診斷code offset956，**不是原8498執行位址或可刷BIN**。8448、979E、19BD4、main9008、resident40000，連同原機記憶體／ROM／最終配置／啟動／BLE OTA仍未閉合。沒有執行目標、HOST模型、ISA模擬或硬體／網路操作。

下一個來源目標為 [ECALL恢復候選](ecall-candidate.json)：8448–8496共78B／35指令，後面另有兩個零bytes。它以mask32執行CSRS0x804，從SP+0讀取mepc，再恢復register frame；特殊CSR語意及trap上下文仍未證。先前80B的有界查詢保留於 [前緣紀錄](ecall-frontier.json)，不當作80B已確認程式碼。

候選新功能是BLE啟動／callback註冊診斷，目前只新增離線來源報告。[原收據索引](publication-provenance.json)保留4份可攜原收據的完整bytes；大型curation原收據仍留本機。[實驗與重播](../../experiments/tsl9-lle-irq/README.md)。commit／push因歷史個資持續暫停。
