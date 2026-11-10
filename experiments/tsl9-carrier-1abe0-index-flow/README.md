# 1ABE0 的 base+index 潛在讀者：條件式交集

離線靜態分析，固定 APP `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`（76,800 bytes，offset 0 = PC `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）。本研究不把 `[0x1abe0,0x1ac00)` 判為 padding，也不聲稱已觀察到讀取。

## 真實指令及條件

`verify.py` 固定完整 consumer `[0xcedc,0xcf96)` 和 setter `[0xd05c,0xd07c)` 的原始指令 bytes，而非僅固定表格；原始指令與逐指令 CFG 另見 `analysis/record-field-transitions-2026-10-25/evidence.json` 和 `experiments/tsl9-APP-residual-access-audit/verify-v1.py`。以下以普通入口 `0xcedc`、有效存取及正常執行為前提：

* `0xcee0` 讀 `0x2000bf38`，為零在 `0xcee4` 返回；非零繼續。`0xceea` 讀 phase `0x2000bf3a`。phase 為 `0xff`，`0xcef6` 不跳轉，進入 `0xcefa`；phase 為 0，經 `0xcf66..0xcf78` 跳至 `0xcefa`；其他 phase 則 `0xcf7a` 設 a4=0。前兩條路 `0xcf0a` 由 `0x2000bf39` 零延伸載入 mode 到 a4。`0xcf7c` 的 `&7` 寫 a3 而非 a4，不能用來限制查表 row。
* `0xcf36..0xcf4a` 更新 record+4，`0xcf3a` 重新讀取該 byte，`0xcf44` 得 `nibble=(byte+1)&15`。`0xcf4e/0xcf52` 算出 `0x1a078`；`0xcf3e/0xcf56/0xcf58` 得地址 `0x1a078 + 16*a4 + nibble`；`0xcf5a` LBU，`0xcf5e` 將所得 byte 寫入 record+3，然後跳往 `0x12a08`。上述 byte 指 **CF3A 實際讀值**，不是呼叫時 record 值；mode 同理指 **CF0A 實際讀值**。記憶體別名可能改變讀值，不可假設輸入互相獨立。
* `0xd05c..0xd07c` 在 `0xd06e` 將呼叫者 A0 低 byte 寫至 mode，該 setter 沒有本地範圍檢查。已選直接呼叫的值為 1、3、5；另一 setter 寫 2、4、5；詳見 `experiments/tsl9-mode-state-writer-contract/README.md`。這些是局部來源，不排除間接呼叫、其他 writer、alias、IRQ 等；亦未證明 setter 到此 reader 的具體時序。不能推定 182–184 實際出現。

## 精確算術交集，不是全域可達證明

由一 byte mode 和 nibble，在 mode 讀取路徑的保守地址包絡為 `[0x1a078,0x1b078)`；與 carrier 的**精確算術交集**是全 32 bytes，必要且充分的採樣值為：

| mode（十進位） | nibble | 讀取地址半開區間 |
|---|---|---|
| 182 | 8..15 | `[0x1abe0,0x1abe8)` |
| 183 | 0..15 | `[0x1abe8,0x1abf8)` |
| 184 | 0..7 | `[0x1abf8,0x1ac00)` |

要使這些組合在普通入口到達 `0xcf5a`，還須 enable 非零、phase 為 0 或 `0xff`、各訪問有效、控制流不中斷，並在實際相應 load 取到表中 mode/nibble；若 phase 為其他值，row 固定為 0，不可能碰 carrier。模式 0..5 亦不碰 carrier。這是對已固定 consumer 的條件式模型：表中每組是否能從真實初始化及呼叫鏈抵達，**未知**；setter 形參可接受任意 byte 不等於有可達呼叫傳入它們。間接進入 consumer 中間、其他讀者和硬體狀態皆未封閉，不排除也不宣稱存在。

## 重播及負測

```
python experiments/tsl9-carrier-1abe0-index-flow/verify.py
python -m unittest discover -s experiments/tsl9-carrier-1abe0-index-flow -p 'test*.py'
```

重播固定全檔 hash、兩段完整原始指令，窮舉 256×16 的數學交集；測試破壞多處 branch/load/索引/基址/setter byte（停用全檔 hash 以獨立測 witness）、全檔 hash mutation、enable/phase 與 carrier 兩端反例、已知小 mode 和非法 byte。模型不是 ISA 模擬、實際執行或完整全程式可達性證明；不產生韌體、不接硬體。保留其他工作。此前 reset-copy 邊界及有限原始引用掃描屬於尚未納入此 checkpoint 的獨立研究，不是本重播的依賴。
