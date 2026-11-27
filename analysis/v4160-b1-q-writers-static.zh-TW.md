# v4.1.60：Q 槽的有界常數來源寫入普查

接續 [Q 槽來源與初始化保存](v4160-b1-q-source-static.zh-TW.md)。前輪只普查標準 SW 的指定位移，本輪加入 **LUI 起點、最多 32 指令的局部定義追蹤**，搜尋 byte／halfword／word 寫入與 Q 四個 bytes 的重疊。兩版候選仍只命中已知 radio parent publisher；沒有找到額外的命中。這個否定結果受下述搜尋界線限制，**不能推出沒有其他 writer、全域 Q 不變或跨事件保存成立**。

## 搜尋結果

| 輸入 | 完整四 byte 半字對齊窗口 | 標準 LUI 起點 | 解碼指令出現次數 | 命中 store PC |
|---|---:|---:|---:|---|
| 原始 APP，分別查兩個候選 Q 槽 | 38,399 | 593 | 4,822 | 無 |
| V1.31 BIN | 95,538 | 2,906 | 26,272 | `0x642cc` |
| V1.31 完整 sparse HEX | 95,605 | 2,906 | 26,272 | `0x642cc` |
| V1.40 BIN | 95,786 | 2,923 | 26,368 | `0x643b6` |
| V1.40 完整 sparse HEX | 95,855 | 2,923 | 26,368 | `0x643b6` |

APP 的每個候選槽搜尋各自產生表中的計數，並非兩次合計。不同 LUI 起點的 prefixes 可以重疊，指令、store 與 literal-base store 計數皆是 **搜尋出現次數**，不是唯一指令數、執行次數或覆蓋率。

V1.31 的 Q 為 `0x20003590`，V1.40 為 `0x200035e0`；命中皆為對齊四 byte store，base 的局部定義得到 `0x20003000`。每個 publisher 有七個 seed witness，分別包含 14、12、10、8、5、3、2 條指令。前六個 witness 也能追到 source literal `0x40025000`；最短的兩指令 witness 沒有來源暫存器的定義，因此 `source_literal=null`。Ledger 將 source literal 放在每個 witness，避免把首筆的來源結論套到其他 witness。

在這些 prefixes 內，也沒有得到數值落在 Q 四個 bytes 內的 ADDI／MV／ADD 地址建構。這不涵蓋由 load、傳入暫存器或未追蹤運算得到的指標，亦不表示 Q 的地址沒有傳給其他程式。

## 方法與停止邊界

[檢查器](check_v4160_b1_q_writers_static.py)在原始 APP、兩個固定 hash 的 BIN，以及 checksum／身分驗證後的完整 sparse HEX 中，逐半字檢查完整的標準 32-bit LUI 編碼。HEX 不補洞，搜尋包含 BIN 終點以外實際捕獲的 bytes。

對每個非零 destination register 的 LUI 起點，保留一段最多 32 條指令的不可變解碼 prefix。查詢 store 的 base 時，向後尋找該暫存器最近的編碼定義：

- LUI／LI 給定 literal；AUIPC 使用名義來源 PC。
- ADDI／MV／ADD 再追溯其輸入定義；只做封閉的整數／32-bit 取模運算。
- 零暫存器為零；load 或其他無法求值的最近定義回傳未知，不能跳過它去沿用較早的常數。
- 不取目標記憶體內容，不推演 store 對 RAM、MMIO、provider 或 callback 的效果。

遇到 call／jump／branch、非允許的非控制指令、未知編碼、較長指令編碼、缺少任何指令 byte 或 32 條上限，該 prefix 立即停止。每個 seed 都必須有一個停止原因，並寫入 [固定 ledger](v4160-b1-q-writers-static.json)。允許的其他指令若寫入暫存器，會形成未知定義；不因「暫時無法算值」而保留舊的已知值。

Store 只在 base 可由上述定義求得時檢查地址，將每個寫入 byte 的 32-bit 取模地址與 Q 的四個 bytes 比較。因此支援窄幅、未對齊、部分重疊與地址尾端 wrap 的搜尋判斷；沒有從此推定硬體允許該存取或指令必定完成。解碼器可辨識的 compressed store 也可出現在 prefix 內，但 seed 僅是標準 LUI，並非所有 compressed 常數建構入口。

這是局部語法定義與地址區間證據，沒有執行或模擬目標 ISA，也沒有建立 mutable register／RAM／MMIO 模型。Prefix 可能從資料或較長指令的中間開始；命中不自行證明是可達 code。已知 publisher 的原指令與呼叫身分另由前輪完整 guard 接回。

## 限制與後續

搜尋不跨越分支、呼叫、未知指令、缺口或上限；不使用起點之前的 register facts。載入所得指標、其他運算、copy／fill 的間接寫入、外部 IRQ／DMA／重入、動態 code 與別名不在這份否定結果內。AUIPC 的值以來源 PC 計算，並未證明複製到 RAM 後的實際執行 PC 或實體映射；數值地址分離也不證明無物理別名。

因此，本輪增加的是有明確停止原因的 writer 搜尋證據，不擴張前輪「同一次選定初始化」的保存定理。較晚 postservice 仍需自己的 Q 保存證書；provider 的 installed 身分、啟動與跨事件順序、poll 進展，以及配置保留／消費釋放／通知保存期都仍未完成。

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。

## 驗證

完整來源、strict HEX 與前輪 ancestry guards 後重算 ledger。42 個封閉 host fixtures 包含三種標準 store 寬度的重疊邊界、改名 base、MV／ADD／AUIPC／C.SW、load kill、call／branch／ECALL 停止、缺口、步數上限及 wrap；另外四個原 publisher 位置的 base／store 擾動必須移除該命中。這些只是 host 搜尋器檢查，不是目標韌體執行。

```powershell
python analysis/check_v4160_b1_q_writers_static.py
python -O analysis/check_v4160_b1_q_writers_static.py
```

全程離線，沒有目標執行、模擬、硬體存取、封包重放或 target network。
