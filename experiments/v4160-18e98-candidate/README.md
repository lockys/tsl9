# V4.1.60 0x18e98 靜態事件候選

固定映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。映像載入位址 0x8000；以下視窗 0x18e98–0x18eb5 對應檔案偏移 0x10e98–0x10eb5。以已索引 r2 唯讀操作：`r2 -q -a riscv -b 32 -m 0x8000 -c "e scr.color=0; pd 10 @ 0x18e98" <BIN>`。

```text
18e98 b7066745 lui  a3, 0x45670
18e9c b7270240 lui  a5, 0x40022
18ea0 93863612 addi a3, a3, 291
18ea4 3797efcd lui  a4, 0xcdef9
18ea8 d4c3     sw   a3, 4(a5)
18eaa 1307b79a addi a4, a4, -1621
18eae d8c3     sw   a4, 4(a5)
18eb0 d4d3     sw   a3, 36(a5)
18eb2 d8d3     sw   a4, 36(a5)
18eb4 8280     ret
```

正立即數得 `0x45670123`；負立即數符號延伸後得 `0xcdef89ab`。四個 32 位寫入依原順序表示成 callback 事件；函數指標與 context 所用物件須在每次呼叫時有效，且不存在資料競爭或其他 C 未定義行為。回呼可能產生額外副作用；若不返回，後續事件不保證發生。原指令正常返回時保留入口 a0，而此 `void` callback 候選不承諾此暫存器結果。候選不是目標 ABI，亦不描述或保證實際位址映射、硬體副作用、例外或執行結果。事件不等於硬體驗證。

`test.py` 檢查完整映像 SHA、完整視窗 bytes、C 檔 SHA pin、位元解碼及獨立 Python 事件 reference 的固定期望，並包含變異負例。**Python 不執行或驗證 C**；C hash 僅固定檔案身分，不證明實作正確。無需編譯 C 或執行／模擬 target：

```text
python -B experiments/v4160-18e98-candidate/test.py
python -B -O experiments/v4160-18e98-candidate/test.py
```
