# V4.1.60：0x18ec4 靜態證據

純靜態分析；**no C / no hardware**。沒有編譯或執行 C、target，沒有模擬、網路或硬體 settings。以下是指令語意，不是實機追蹤，也不推定暫存器名稱、硬體效果或可終止性。

## 固定輸入與座標

`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。RV32 little-endian，含 compressed；分析 base `0x8000`，檔案 offset = PC − `0x8000`。視窗為半開區間 `[0x18ec4, 0x18ef2)`，offset `[0x10ec4, 0x10ef2)`，46 bytes，SHA-256 `40e81eda78577543dd451a59487376d58352cb623c796194e0fcc9c12b23995d`。`0x18ef2` 是下一條指令，不屬視窗。hash 固定內容，不證明來源。

唯讀 r2 6.2.4（無 `-w`）：

```
r2 -q -a riscv -b 32 -m 0x8000 -c "e scr.color=false; pd 35 @ 0x18eb0" <bin>
```

## 指令與控制流程

```
18ec4 b7270240  lui  a5,0x40022
18ec8 984b      lw   a4,16(a5)
18eca b7060200  lui  a3,0x20
18ece 137505f0  andi a0,a0,-256
18ed2 558f      or   a4,a4,a3
18ed4 98cb      sw   a4,16(a5)
18ed6 c8cb      sw   a0,20(a5)
18ed8 984b      lw   a4,16(a5)
18eda 13670704  ori  a4,a4,64
18ede 98cb      sw   a4,16(a5)
18ee0 d847      lw   a4,12(a5)
18ee2 058b      andi a4,a4,1
18ee4 75ff      bnez a4,0x18ee0
18ee6 984b      lw   a4,16(a5)
18ee8 8176      lui  a3,0xfffe0
18eea fd16      addi a3,a3,-1
18eec 758f      and  a4,a4,a3
18eee 98cb      sw   a4,16(a5)
18ef0 8280      ret
```

- `a5 = 0x40022000`；32-bit `lw/sw` 的有效位址分別是 `0x40022010`、`0x40022014`、`0x4002200c`，均 4-byte aligned。`a0 & 0xffffff00` 對齊的是**寫入的值**，不是將上述存取位址再對齊。
- 首次讀 `0x40022010`，OR `0x20000` 後寫回；寫入遮罩後的 `a0` 到 `0x40022014`；再**重新讀取** `0x40022010`、OR `0x40`、寫回。這些是分開的 read-modify-write，不能假設中間的值不變或操作具有原子性。
- poll 從 `0x18ee0` 每次重新 `lw` `0x4002200c`，取 bit 0；非零時 C.BNEZ 返回 `0x18ee0`。讀到 bit 0 為零才落入 `0x18ee6`；沒有可見的計數上限或 timeout，故不保證終止。
- 結束 poll 後又**新讀** `0x40022010`，以 `0xfffdffff` 清除 bit 17，寫回並 `ret`；這不是重用先前的讀值，也不宣稱清除 bit 6 或其他硬體狀態。

## 驗證

```
python experiments/v4160-18ec4-evidence/verify.py
python -O experiments/v4160-18ec4-evidence/verify.py
python -m unittest discover -s experiments/v4160-18ec4-evidence -p test_verify.py
python -O -m unittest discover -s experiments/v4160-18ec4-evidence -p test_verify.py
```

可對 `verify.py` 傳入其他 bin 路徑。檢查整檔長度及 SHA、視窗完整 bytes，並從實際視窗位元解碼 C.BNEZ 的來源暫存器與 signed displacement。測試直接呼叫視窗/branch 檢查，令負例不被整檔 hash 先行拒絕所掩蔽；測試不修改 bin。
