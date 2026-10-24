# 主迴圈佇列與接收路徑

[English](readme.en.md)

接通12C58佇列消費與17002旗標消費入口，重用10個既有C/C++單位的**1464B／509指令／59區塊**。C11／C++17原位址碼核對吻合，新增68筆具型別參照。

主元件為**7100B code＋456B data、514個有大小FUNC、25個真實入口別名、424RELA、16UND**，C／C++產物相同。原5636B code與456B data、62個選定非零向量綁定保持不變。兩個主入口接通後，又展開12ABE、14D2E兩個分派依賴，因此UND總數仍為16。

完整[record_program.c](../../src/native/receive/record_program.c)保留於src。為重用父元件中已驗證的34B disarm，本輪[可重現C選取](../../experiments/tsl9-main-queue/derive-selection-v1.py)僅移除同一函式定義，再以相同編譯profile編譯；其餘函式bytes與參照都與完整來源相同。95個curated C/H檔及manifest未改變，來源投影仍合計138組／276物件，另有2個選取用編譯物件。

[原始AUIPC／ADDI](queue-layout.json)在原PC推得2000C038。12B參數與32索引比較可描述名義384B範圍；VMA=0元件的實際配置、RAM初始化、resident保存暫存器與實機迴圈界限仍未證明。

1973C的clock-fields及包含9A42的irq完整來源物件未通過本輪原碼核對，沒有接入；這也不代表95個來源的copy比對能證明全數與原廠相同。[下一步](next-providers.json)記錄實際錯誤、完整範圍待查與14D2E的28B表格。

~~~sh
python3 experiments/tsl9-main-queue/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-queue/build/providers-v1
python3 experiments/tsl9-main-queue/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-main-queue/build/component-v1
python3 scripts/check-main-queue-publication.py
~~~

[摘要](summary.json) · [剩餘提供者](pending-providers.json) · [匯出來源](publication-provenance.json)

可研究被動佇列占用／丟棄原因診斷，目前未實作。**這是未解析、VMA=0的ET_REL，不是可燒錄BIN。** 原機、installed ROM／ABI、完整記憶體／IRQ及BLE OTA未證明。未執行目標、HOST model或ISA，未接觸硬體、網路，未commit／push；歷史個資問題仍在。
