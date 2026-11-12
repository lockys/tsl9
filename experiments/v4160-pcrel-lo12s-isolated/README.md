# RV32 PC-relative LO12_S 單一 pair 位元實驗

純 Python；不讀取 ELF、不產生或修改 BIN，不執行目標、模擬、編譯，亦不連接網路或硬體。`pcrel.py` 將整數 instruction 作為輸入及輸出，沒有檔案寫入功能。

## 既存證據與邊界

`experiments/tsl9-original-layout/build-v31.py` 的 `validate_original` 支援 23 HI20、24 LO12_I，並查找 HI anchor；沒有處理 25 LO12_S。另一份獨立既存證據 `analysis/v4160-residual-code-2026-10-20/native/generate-residual.py` 記錄 F668 HI20 指向 `__tsl9v4160_ram` 0x20004000 加 0x7f99，F66C 的 25 LO12_S 指向 F668 anchor；該目錄 README 將此標為既存元件的 relocation 證據，而非原始 BIN 自帶 relocation。

唯讀 r2 6.2.4 核對原始 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`），依該專案 base 0x8000，檔案 offset 0x7666 對應 PC 0xf666：

```text
r2 -q -n -a riscv -b 32 -c "px 12 @ 0x7666; pd 4 @ 0x7666" <原始BIN>
7666  8547       li a5, 1
7668  17d7ff1f   auipc a4, 0x1fffd
766c  a308f792   sb a5, -1743(a4)
7670  8280       ret
```

r2 顯示的是檔案 offset；加 base 才是上述 PC。測試固定原始 hash 和這 12 bytes；以既存 addend 重建兩個原始指令。原始 BIN 的指令位元本身不證明 ELF relocation、符號或執行效果。

## 模型

以 HI 的 AUIPC PC 為 anchor，而非 store 自身的 PC。`delta = signed32(target + addend - hi_pc)`，即先模 2³² 再解讀有號；`HI20 = ((delta + 0x800) >> 12) & 0xfffff`，`LO12 = sign_extend(delta & 0xfff)`。S immediate 的高七位置於 [31:25]、低五位置於 [11:7]；其他位元保留。decode 使用 AUIPC 的有號高位及 S 的有號低位，最後模 2³²。

此模型只檢查 AUIPC 與 integer-store opcode、輸入字長與 signed LO 範圍；不驗證 store funct3、暫存器資料流、指令邊界、ELF symbol/addend/relocation 關聯、anchor 唯一性或完整 guard，不是 linker，也不能證明整個韌體正確或可刷寫。

## 測試

在此目錄執行：

```text
python -B -m unittest -v
python -B -O -m unittest -v
```

涵蓋全部 4096 個合法 LO、越界與錯 opcode、HI rounding 正負界線、anchor 偏移和 RV32 wrap；測試與實作不依賴 Python `assert` 陳述式。需要上述原始 BIN；缺少或 hash 不同即失敗。
