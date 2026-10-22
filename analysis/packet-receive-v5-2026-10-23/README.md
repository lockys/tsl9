# Packet receive v5

[English](readme.en.md)

官方 ID2966 V4.1.60 的 `[0x16A7C,0x16B0A)` 已重建為 C 算術與明示架構 ports：C11／C++17 皆為 142B／52 指令，單一 12B restore 結尾。**這是待連結的元件證據；重建韌體尚未成功刷入及在原機正常執行。**

| 核對 | 結果 |
| --- | --- |
| 真實 FUNC／配置 | entry14B、body116B、finish12B；部分連結位置0／14／130，無填補 |
| 原碼投影 | 排除4個JAL與2個分支後120B完全相同；SHA `528b69f7ec290450aa7b0338bdfbf25b88571693b0f2142199ccdb37c34479f6` |
| 實際重定位 | 6筆、addend0；3個SPI呼叫、1個ring呼叫指向2個genuine UND，2個分支指向已定義finish FUNC；沒有ABS替身 |
| 重要限制 | 全部6個控制指令的immediate仍未套用；不能把投影相同說成完整142B機器碼相同 |
| 編譯／重播 | 每語言2個實際ELF、9個輸入、10個產物、5個完整配方、source/header MD closure及41個負例；strict readiness拒絕 |

收據：[C](receipts/packet-c.json)／[C++](receipts/packet-cpp.json)，為已產生可攜路徑的原始JSON逐位元組副本。[verify.py](../../experiments/tsl9-packet-receive/verify.py) 驗證完整ELF、52條typed operations、完整normalized IR、原廠投影與實際owner／relocation，不執行韌體。IR只排除前兩行產生端路徑並統一LF；本機raw IR／logs未上傳。原始BIN未修改。

v3修正A1初始化依賴，v4修正DLC使用A4與A0 residue／ID順序，但仍為154B／58指令。v5將唯一結尾獨立為真正FUNC，兩條拒絕分支使用symbolic relocation。舊版保留為失敗實驗，不改寫收據；原始雜湊與換行差異見[summary.json](summary.json)。

來源：[v5](../../experiments/tsl9-packet-receive/src/packet_receive.v5.c)；正式配方與使用方式見[實驗入口](../../experiments/tsl9-packet-receive/README.md)。一般C呼叫、alias／IRQ／fault、完整ring／resident ABI、晶片身分及OTA均未證明。[下一個ring目標與功能線索](ring-next.md)。
