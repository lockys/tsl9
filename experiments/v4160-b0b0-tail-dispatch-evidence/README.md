# V4.1.60 `0xb0b0` 尾跳上游：局部表格證據

僅分析固定 BIN `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。raw offset 0 對應 PC `0x8000`。半開窗口 `[0x155d0,0x15650)`、`[0x1a9f4,0x1aa00)`、`[0x16266,0x16296)` 的完整原始 bytes 固定在 `verify.py`。

## 局部推導

以索引的 r2 6.2.4 唯讀反組譯（以下命令由 repo 根目錄執行；Windows 路徑須按環境引用）：

```text
C:\Users\locky\Tools\radare2\bin\r2.exe -n -a riscv -b 32 -m 0x8000 -q -c "e scr.color=0; pd 46 @ 0x155d0; px 12 @ 0x1a9f4; pd 21 @ 0x16266" firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
```

從 `0x155d0` **順序進入**，記當時完整 32 位 `a0=A`。先讀 `*(gp+84)` 得指標，再讀其 `+4` byte；若 bit 3 為 1，只有 `((A+6)&255) <= 2` 才通過 `0x155f2`，否則跳 `0x1578c`。接著讀 `*(gp+358)` byte：非零時清零並尾跳 `0x18110`，不走本 dispatch。若為零，`s2=A-1`，先以 `(s2&255)<=7` 決定是否呼叫 `0x9124`；本研究三個值的低 byte 是 `c1/c2/c3`，故均跳過該呼叫。然後 `index=(A-1)&255`，僅 `index<=252` 可通過 `0x15638`；253–255 跳 `0x1578c`。

`0x1563c` 的 AUIPC 以**自身 PC**為基準：`0x1563c + (5<<12) + 184 = 0x1a6f4`，不是以後續 ADDI 或 JR 的 PC 為基準。`0x15644..0x1564e` 取 `word_le32(0x1a6f4+4*index)`，與表基址相加（RV32 取低 32 位），JR/JALR 再清除 bit 0。這些 word 是相對**表基址**的位移，不是絕對指標，也不是相對各 entry 位址。

| A 低 byte | index | entry 位址 | LE bytes / signed displacement | 目標 |
|---|---:|---:|---|---:|
| c1 | c0 | 1a9f4 | `72 bb ff ff` / -17550 (`-0x448e`) | `0x16266` |
| c2 | c1 | 1a9f8 | `82 bb ff ff` / -17534 (`-0x447e`) | `0x16276` |
| c3 | c2 | 1a9fc | `92 bb ff ff` / -17518 (`-0x446e`) | `0x16286` |

以上三個低 byte 下 `(A+6)&255` 分別為 `c7/c8/c9`，不滿足前述 bit 3 為 1 的放行條件，因此**必須**該 bit 為 0；另須 `gp+358` 的 byte 為 0、相關指標與讀取有效，並實際從指定入口順序走到此處。`gp` 的值與初始化、入口 `a0` 的來源及實際可達性均未確認；不能據此宣稱某輸入在裝置上必然觸發。本結論不涵蓋其他入口、例外、記憶體別名或其他映像。

三個目的地固定窗口分別恢復 s0、ra、s1、s2，令 a0 為 1、2、4，調整 sp 後以 JAL x0 尾跳 `0xb0b0`。這與 `experiments/v4160-b0b0-direct-edge-evidence/README.md` 的尾跳及 `0xb0b0` store 局部證據銜接；該證據已納入遠端提交 `ed318d53ae678a73ef70b4755372efaf101a45b3`。本實驗自行固定相同尾跳 bytes，不依賴該目錄。窗口固定不等於驗證 stack 有效、實際返回或硬體寫入。

## 重播與範圍

```text
python -B experiments/v4160-b0b0-tail-dispatch-evidence/verify.py
python -B experiments/v4160-b0b0-tail-dispatch-evidence/test_verify.py
python -B -O experiments/v4160-b0b0-tail-dispatch-evidence/test_verify.py
```

驗證器以全檔 hash、長度及逐 byte 窗口檢查固定映像；獨立解碼 AUIPC/ADDI 即時數及三個 signed table word 並檢查位址算術。其他指令語意依上列 r2 靜態解讀，並非完整獨立解碼或 CFG 證明。測試逐一突變窗口每個 byte、逐長度截斷，直接測局部檢查避免 hash 掩蓋缺陷；另測身分、算術負例，normal 與 `-O` 均不依賴 `assert`。未執行或模擬 target，未編譯、使用硬體或網路、修改工具設定。
