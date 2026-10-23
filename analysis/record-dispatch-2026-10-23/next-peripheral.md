# 下一段：18CA4 暫存器傳輸操作

[English](next-peripheral.en.md) · [72條原始指令](next-peripheral.json) · [範圍契約](next-peripheral-contract.json)

已界定 `[18CA4,18D78)` 的212B／72指令：一個RET後有三個仍可到達的cold block；所有直接控制目標皆在範圍內。下一個18D78入口已有其他原始碼證據，本輪不跨入它。尚未重建此段C，亦未把暫存器配置當成實體硬體身分證明。

| 原始範圍 | 已確認操作 | 保留的界線 |
| --- | --- | --- |
| 18CA4..18CC4 | 三次fresh `[A0+8]`，依序測bit26／27／28；選0／1／2或回4 | 不能合成單次snapshot；硬體非同步行為未知 |
| 18CC6..18CEA | selector×16；位移ID與輸入bytes8／9，更新selected+384 | standard／alternate path及fresh RMW次序需完整保留；A0在此被覆寫 |
| 18CF0..18D0A | 原record byte10與15做AND並寫回，分開讀寫register+388 | 不新增長度≤8的guard；不將原record視為不可變 |
| 18D0E..18D56 | 依12、11、13、14、16、15、17、18讀八個bytes，更新+392／396；最後+384 OR1 | 讀取次序、A6只在alternate path改寫，以及RMW不能簡化 |

12A50呼叫端提供base `40006400`。這段符合「三組暫存器資料送出」的候選解讀；仍未確認周邊名稱、實體傳送或座椅／免打擾對應。可新增的離線診斷是展示selector、原始／masked長度與實際被讀取的八個bytes，並明示未觀察到硬體送出。
