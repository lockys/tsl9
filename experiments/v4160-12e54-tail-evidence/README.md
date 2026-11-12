# V4.1.60：0x12e86 tail 與 0x12e54 靜態證據

僅使用 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。原始 BIN 以位址 0x8000 映射，故檔案偏移 = 指令位址 − 0x8000。以索引指定之 `C:\Users\locky\Tools\radare2\bin\r2.exe` 唯讀反組譯：

```
r2.exe -a riscv -b 32 -m 0x8000 -q -c "e scr.color=false; pd 80 @ 0x12e54" <BIN>
```

以下是指令順序的條件性描述，不證明任何入口或呼叫可達，也不推論呼叫語意、C、ABI、執行時記憶體映射或硬體效果。所有未知呼叫可能不返回、改變暫存器或記憶體；不得假設 stack、資料、函式指標及呼叫副作用互不 alias。計算為 RV32 模 2³²；指令載入、儲存及跳轉是否成功均未證明。

## 從 0x12e86，條件性地走到 tail

設入口 sp=S、ra=R、s0=F。0x12e8a 先令 sp=S−16，接著 `lw a5,72(0x40000)` 取得未知間接目標，寫入 word `[S−8]=F`，以 AUIPC 和 ADDI 算出 s0=0x2000c494，再寫入 `[S−4]=R`，並以 a0=s0、a1=0、a2=256 間接呼叫該目標；jalr 將 ra 設為 0x12ea4。此呼叫內容未知，必須保留；後續若呼叫返回，其實際 s0 不一定仍為 0x2000c494。

令返回後 s0=T，後續直接儲存依序為：

| 指令位址 | 寫入 |
|---|---|
| 0x12ea8 | byte `[T+255]=0x5a` |
| 0x12eb4 | word `[T+0]=0x0b431402` |
| 0x12ebe | word `[T+4]=0x0d450c44` |
| 0x12ec8 | word `[T+8]=0x2b0c2c0a` |
| 0x12ed0 | word `[T+12]=0x5f1f501e` |
| 0x12eda | word `[T+16]=0x2a211e20` |

加法均取模 2³²。只有額外假定呼叫保留 s0，T 才是 0x2000c494；也不能假設上述儲存沒有覆寫保存區。接著從當時 sp+8 載入 s0、sp+12 載入 ra，sp 加 16，0x12ee2 的 `jal x0,0x12e54` 不寫 ra，**不是 fallthrough 到 0x12ee6**。若呼叫破壞 sp 或保存區，還原值不保證等於 F、R；即使 s0 保留，儲存也可能 alias 保存區。

## 0x12e54 前綴至 return

以 tail 實際交付的 sp=P、ra=Q 為輸入（直接進入時也可如此命名）。先從 `[0x4004c]` 載入未知目標，再 sp=P−272，word `[P−4]=Q`；a0=sp、a2=256、a1=0x2000c494（0x12e66 的 AUIPC 加 1582）。0x12e6e 的 jalr 呼叫未知目標，ra=0x12e70。若返回，設當時 sp=U：a0=0x08077900、a1=U，0x12e7a `jal ra,0x9c0a`，ra=0x12e7e；該呼叫的 a2 未知，此直接目標的內部效果同樣未知。若再返回，從當時 sp+268 載入 ra，sp 加 272，`ret` 即跳至載入 ra 清除最低位之位址；只有兩次呼叫及任何 alias 均未破壞必要 sp/保存值等條件下才回到 Q。沒有順序 fallthrough 到 0x12e86。初始 a5/a0/a1/a2 不須保留；實際間接呼叫需要可讀函式指標與可用 stack 等條件，並不等於證明其成立。

## 驗證

`verify.py` 釘選全檔 hash、長度及兩個完整指令 byte window `[0x12e54,0x12e86)`、`[0x12e86,0x12ee6)`，獨立按 RISC-V immediate 位元算 AUIPC/ADDI、常數與 JAL 目標；0x08077900 從 0x12e70 的 LUI 與 0x12e76 的 ADDI 解碼，並檢查其間 0x12e74 的 compressed 指令。其餘指令語意來自固定 bytes 的 r2 靜態反組譯，不是模擬器；不推定呼叫的副作用。可傳 BIN 路徑作為唯一參數。測試逐一變更及截斷每個窗口 byte，另測 hash 與地址運算負例：

```
python -B experiments/v4160-12e54-tail-evidence/verify.py
python -B experiments/v4160-12e54-tail-evidence/test_verify.py
python -B -O experiments/v4160-12e54-tail-evidence/test_verify.py
```

未編譯、執行或模擬目標，亦未接觸網路或硬體設定。
