# V4.1.60：0x2000beeb 局部消費證據

僅靜態分析 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；raw BIN 映射基址 0x8000，VA 對應檔案 offset = VA − 0x8000。未執行目標、模擬、編譯或接觸硬體。

## 可重現

使用 tool-index 的 `C:\Users\locky\Tools\radare2\bin\r2.exe` 唯讀開啟：

```text
r2.exe -n -a riscv -b 32 -m 0x8000 -q -c "e scr.color=0; pd 120 @ 0xae0e; pd 12 @ 0x81b0; pd 6 @ 0x81de; pd 2 @ 0x8440" <BIN>
python -B experiments/v4160-beeb-consume-evidence/verify.py
python -B experiments/v4160-beeb-consume-evidence/test_verify.py
python -B -O experiments/v4160-beeb-consume-evidence/verify.py
python -B -O experiments/v4160-beeb-consume-evidence/test_verify.py
```

程式固定全檔長度與 hash，另外逐 byte 核對半開區間 `[0xae0e,0xaf4c)`、`[0x81b0,0x81ca)`、`[0x81de,0x81ee)`、`[0x8440,0x8446)`。測試逐 byte 各翻轉一個 bit，分別直接檢查 window 與完整驗證，並對各 window 每個截斷位置測試；另測全檔尾端變更及增減長度。地址解碼單獨檢查兩條 AUIPC 配對指令的 opcode、暫存器及立即數，並以各自 PC 算術驗證，含搬移配對的測試。不靠 Python assert，故 `-O` 同樣驗證。

## 限定 CFG 與副作用

以下僅描述指定靜態切片中的指令，假設指令正常完成、呼叫正常返回；不是證明入口可達、記憶體有效、無中斷或並行寫入。

* 入口 0xae0e 保存暫存器、以輸入指標為 s0；0xae1a 前後有對輸入位址及另一 PC-relative 位址的讀寫，0xae48 可能呼叫 0xad48。0xae4c 讀 `[s0]` 半字，須等於 921 且 `[s0+11]` 等於 1 才進入 0xae62，否則跳 0xaf4c。0xae6e 從 `[0x4004c]` 取出的函數指標間接呼叫，參數為 `sp+4, s0, 12`；不能假定其實作或副作用。
* 0xae74/78 讀另一 byte：`0xae74 + 0x20001000 + 109 = 0x2000bee1`；0xae7c 讀 `[gp+184]`。依該 byte 和該 word，可能 0xae86 呼叫 0x81b0 後寫 `[gp+184]`，或在 0xaf42 清除該 word。0x81b0 自 `[0x4007c]` 取函數指標間接呼叫，返回值乘 10 取低 32 位，再邏輯右移 4；其外部 callee 副作用未知。
* 0xae98 對 `[sp+12] & 0x3c` 比較 0x10；不相等走 0xae9c，s2 清零後進 0xae9e；相等走 0xaf0a 呼叫 0x81de（讀 `[gp+84]` 指標的 offset 5，取低兩位加一），結果 bit 1 為零則走 0xae9c；否則呼叫 0x8440（讀 `[gp+364]`），結果為零同樣走 0xae9c。非零時呼叫 0x81b0，將返回值減 `[gp+184]` 後取低 32 位，無號比較門檻 0x2edf，超過走 0xae9c，否則修改 `[sp+12]` 位元並直接跳 0xae9e，保留 s2 非零。
* 0xae9e `auipc a5,0x20001`，0xaea2 `lbu a5,77(a5)`：`0xae9e + 0x20001000 + 77 = 0x2000beeb`。0xaea6 若讀值為零直接到 0xaebc；非零則 0xaeac 將 6 寫 `[gp+188]`，0xaeb0 將讀值加 3 的低 byte 寫 `[gp+189]`，然後 0xaeb4 `auipc a5,0x20001`，0xaeb8 `sb zero,55(a5)`：`0xaeb4 + 0x20001000 + 55 = 0x2000beeb`。清除條件是該次 LBU 的結果非零，並非原子 read-and-clear。
* 0xaebc 重新讀 `[gp+188]`：非零則減一寫回，依 `[gp+189]` 低四位改寫 `[sp+12]`，再更新 `[sp+13]`；為零則 0xaf48 根據 s2 決定是否仍進後續處理。0xaefa 呼叫 0xed00，回傳低 byte 寫 `[sp+14]`；0xaf04 呼叫 0x12a08，兩者的內部行為和副作用未在本證據中約束，之後跳 0xaf4c，切片到此為止。

`gp`、`sp`、`s0` 的實際值未固定，不能排除其指向的區域互相 alias 或 alias 目標 byte；間接和直接呼叫也可能改變記憶體。故即使局部 store 寫零，也不能推論此 byte 之後必為零，或所有路徑上每個非零值恰好消費一次。未枚舉所有讀寫、caller、外部 callee 或全域性質，也不推論硬體語義、事件意義及 runtime 行為。
