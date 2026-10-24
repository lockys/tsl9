# 原廠啟動與時鐘碼重建

[English](readme.en.md) · [結果](summary.json) · [C/C++ 來源](../../src/native/startup/boot_original.c)

已將原廠 header、預設入口、reset、中斷跳板及完整時鐘路徑整理為同一份 C11／C++17 來源。99 個架構區域不是 99 個一般 C ABI 函式。

| 範圍 | 已確認的離線證據 |
| --- | --- |
| 8000–8038、18630–18834 | 572B／212 指令，含原廠61個自迴圈、12個完整寬度NOP與EBREAK |
| 1874A–18834 時鐘碼 | 完整234B／93指令，含18830的cold store與回到187CA的跳躍 |
| 1AB60–1ABE0 初始化資料 | 原有C陣列編譯所得的完整128B；只取該section，排除診斷用BSS／stack |
| 真實部分連結 | C／C++產物相同，572B code＋128B data、82 RELA，仍有3個UND；沒有ABS provider替身 |

所有選定指令在**純資料的原位址重定位驗算**後與原廠相同；這不是執行觀察。完整來源檢查為79個C/H、53個單位、106組比對／212個物件；先前104組結果及625筆產物紀錄保持一致。

Reset中的靜態常數為GP=20004000、SP=20010000，複製來源1AB60，zero結尾2000C958；這不證明實體RAM容量或ownership。mstatus使用CSRS mask1888，不能解讀成最終值必定等於1888。新來源保留GP／SP／CSR／MMIO與private register埠；沒有把它們改成一般C呼叫慣例。

仍缺向量資料8038、主程式入口9008與駐留ROM40000；也尚未證明向量／IRQ上下文、原機ROM、最終記憶體配置、啟動或BLE OTA相容性。產物是VMA0的ET_REL，**不是可燒錄BIN**。舊232B時鐘診斷來源保留作歷史參考；長度與原碼不同本身不證明功能錯誤。

[證據來源索引](publication-provenance.json)保存四份可攜式原收據的原始bytes與雜湊；大型完整來源收據僅保留本機，沒有改寫原收據。[向量資料前緣](vector-frontier.json)只整理8038起的72個word，未宣稱完整表長或硬體IRQ數量。

候選新功能：離線映像相容性描述檔，以及唯讀啟動／時鐘診斷。兩者都須先取得完整映像與暫存器語意證據，目前未加入原機執行流程。本輪沒有執行目標／HOST模型／ISA模擬，也沒有硬體、網路或負例操作。

[實驗及重播方式](../../experiments/tsl9-original-startup/README.md)。本次為未提交工作目錄；因已確認歷史個資，commit／push仍暫停。
