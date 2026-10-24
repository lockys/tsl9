# 通道與功能分派的程式／表格整合

[English](readme.en.md)

選定2736B code＋60B相對表，保留15個真實表格目標與698筆主元件參照。重用父元件26B時鐘區塊及C6A8入口；C選取的其餘函式bytes與參照均核對相同。詳見[分析與重播指令](../../analysis/dispatch-tables-2026-10-24/README.md)。

目前採用providers-v2與component-v2；第一個重複定義嘗試保留為未接受資料，component-v1保留為C6A8綁定前的83UND階段。未執行舊verify()／negative函式或目標／HOST model／ISA；無硬體或網路操作，不產生可燒錄BIN。
