# v4.1.60：comparator 串接與 callback 尾段 wrappers

本次完整核對兩個尾段 wrapper，新增 **308 bytes** 原始指令證據；另重播兩份既有 72-byte comparator，共 **144 bytes 重用**。兩者合計 452 bytes／160 條指令。既有 C 重建覆蓋率不變。

| 本體 | V1.31 entry／FLASH source | V1.40 entry／FLASH source | 每版 bytes／指令 |
|---|---|---|---|
| byte range wrapper | `43e6a` | `43ef6` | 36／15 |
| event wrapper | `43932` | `439be` | 118／42 |
| 既有 comparator | `20000442`／`406b2` | `20000442`／`406f2` | 72／23 |

[完整 ledger](v4160-comparator-tail-static.json) 記錄兩版 literal operands、SHA-256、完整 CFG、calls／stores、圖路徑、參數及整數證據。全程僅離線讀取原 bytes、解碼與檢查主機圖／整數，沒有執行或模擬目標 ISA、provider、比較、timer、copy、控制欄位、FENCE 或裝置。

## Comparator 的 1 不是無條件「六個 bytes 相等」

完整 comparator 已有 `analysis/wch-resident-candidate-2026-10-21/memcmp-port-review/check-review.py` 及 resident-entry 的證據。兩版 72 bytes 相同，SHA-256 為 `a9dbd2b47ccefe55ab45f0b4e5a073d7aeb00f42dbe503191a75b6b66efff3aa`。這次重用，沒有重算為新覆蓋。

來源依 startup first-copy operands 映射，在 **RAM PC `20000442`** 解碼；不是已安裝 RAM、實際 startup completion 或後續內容保持的證明。

入口 A0=P、A1=Q、A2=n（完整 uint32）。它先讀並保存 `U32[4002420c]` 至 A4，寫零並 FENCE.I，**之後才檢查 pointer／length**。

- 任一 pointer 為 null，或 n=0：沒有 payload read，正常返回完整 word **1**。
- 兩個 pointer 非 null、n>0：每輪先 fresh 讀左 byte，再 fresh 讀右 byte。第一個 mismatch 返回 **0**；n 對觀察都相同才返回 **1**。

這是帶有 null-success 特例的 boolean equality，不是 ISO `memcmp` 的負／零／正字典順序。P=Q 沒有特殊捷徑，仍會讀兩次；來源可能在兩次觀察間改變，不能推論原子 snapshot。

兩個退出點都將原先保存的控制 word 寫回，沒有退出後的 FENCE。正常返回的局部 restore 不是實際硬體恢復、外部干擾處理或異常存取時恢復的保證。雖然沒有以 P／Q 作 base 的 payload-store 指令，固定控制位址仍可能與來源 alias，因此不能宣稱物理來源永不被修改。

index 從 0 開始，每對相同後加一，與完整 n 比較。在普通指令語義、每次存取有效完成前提下，最多 n 對／2n 次 byte reads；n>0 時 index 不會先 wrap。這是 index 算術，沒有執行這個目標迴圈，也未證明 pointer 加 index 後的地址有效。

此 leaf 無 frame／call，只改 A0、A3～A6，本機不寫 A1、A2、A7、SP、RA 或 S registers，也沒有直接保存輸入 pointer 的 store。這些局部性質不等於整條鏈沒有保存 pointer 或物件生命週期已成立。

## 與 lookup 的六-byte 呼叫串接

沿用 [N+136 callback／lookup 證據](v4160-n136-predicate-static.zh-TW.md)，lookup 的 compare 參數是 `(query+2,node+4,6)`，回覆恰等於 1 才選擇 node。

在有效、非 wrapping、non-null 的 query／node 範圍與 matching comparator 前提下，1 才表示六對 fresh observations 相等；query 至少需要 8 bytes，node 的比較範圍至少 10 bytes。next+60 的 word read 另外需要 64 bytes，成功 match 路徑本身不讀 next。

若缺少 nonwrap／validity 前提，derived pointer 可能為零，而 comparator 直接返回 1；不能把服務回覆單獨當作可讀 extent 或六-byte equality 的證明。鏈表無環、node ownership、N′+132 保存後仍有效及實際 provider 綁定仍未知。

## Byte wrapper：callback 的 N′+12 可條件性界定為 5～15

完整 byte wrapper 是 `43e6a..43e8e`／`43ef6..43f1a`，剛好結束於既有 U16 wrapper 入口，兩者沒有重疊。byte wrapper 為 36 bytes／15 instructions，含最後的 AND255；不是 36 bytes／16 instructions 的 U16 wrapper。

frame32 保存 RA、S0 及 entry A1；S0 保存 entry A0=A。唯一請求是既有完整 word source `433a8/43434`。令其實際 U32 回覆為 R，entry A1=B，則：

```text
d = signed32((B-A) mod 2^32)
reply = low8(A + floor(d × unsigned(R) / 2^32))
```

原指令是 **MULHSU**：第一運算元有號、第二運算元無號。不能換成 MULHU，也不能在 B<A 或 subtraction wrap 時直接套一般有序區間結論。wrapper 本體只有 frame stores，但 source 具有既有控制欄位、狀態更新及 optional callback 路徑，並非無副作用的常數來源。

當前 callback 明確傳 `(5,16)`，d=11，任意 U32 R 均有 `0 <= floor(11R/2^32) <= 10`，所以回覆為 **5～15**，之後由 callback 存入 N′+12。這個結論仍需 matching source／callee 保存、frame 及存取前提；沒有假定 randomness、uniform distribution、實際 seed 或物理單位。

## Event wrapper：保留原始參數與 then-live A2 的區別

event wrapper 完整 118 bytes／42 instructions，局部 CFG 無環；frame32 保存 RA、S0～S3。

它先保存 entry A0 至 S0、entry A1 至 S3、entry A2 至 S1，以及原控制 word 至 S2；然後寫零控制欄位並 FENCE.I。

1. 呼叫 `43728/437b4`，本機 A0／A1／A2 都是入口值。它的回覆沒有在 wrapper 內被檢查。
2. 恢復原始 A0、A1，再請求 **`20000314`，兩版都是同一 RAM 位址**。這裡 **沒有恢復 A2**：A2 是第一次 callee 返回後的 then-live 值，不能假定仍等於入口 A2。
3. 將第二次服務完整回覆捕捉為 R。R=0 就跳過乘法及 R+4 的 store；R 非零才進入數值路徑。

matching `20000314` 的既有本體只使用 A0／A1；未知 installed binding 仍可能觀察其他暫存器，因此完整保留 then-live A2 邊界。它是 timer 的 30-byte lookup，與先前 `2000202c/20002084` 的 76-byte query lookup 不同。

第一個 timer 可以返回拒絕，第二次 lookup 仍可能找到既有 node；不能從 wrapper 的 0 返回推論本次 timer 建立成功。timer／lookup 的既有完整證據是重用內容，不增加這次 308 bytes。

## 64 位乘法與進位形成，尚未提升為 quotient 證明

R 非零時，fresh H=`U16[2000323c/2000328c]`，K 使用 **S1 保存的原始 entry A2**。原指令用 MUL lowword、MULHU highword、lowword 加 800、SLTU 偵測 carry，再加至 highword，形成：

```text
A1:A0 = H × K + 800
A3:A2 = 0 : 1600
```

H<=65535、K<=2³²-1，乘積加 800 小於 2⁴⁸，不會溢出 64 位。當前 callback 的 K<=131070，整對小於 2³³，highword 只可能是 0 或 1。carry 確實可能出現：H=65535、K=65537 時乘積 lowword=`ffffffff`，加 800 後 lowword=799、carry=1。

下一個請求為 `6df1a/6e10a`，兩版位址差 496。它已有完整結構證據，但僅有參數對及結構，不能單獨升級為算術 ABI／quotient 公式證明。本次只確定 **實際回覆 A0 被存入 R+4**；R 至少需 8-byte 有效範圍，仍須保持 pointer、frame、S registers、nonalias 與 child-return 前提。

正常尾段以捕捉的 R 計算 `SEQZ(R)<<3`，所以本機返回值恰為 **R=0 時 8，R!=0 時 0**，與最後算術服務的 A0 回覆無關；退出前寫回原控制 word。callback 也沒有使用這個 wrapper 的最終 status 作為自己的最終回覆。

## 重播與剩餘工作

[Checker](check_v4160_comparator_tail_static.py) 驗證 160 次 instruction mutations、4 次 MULHSU↔MULHU 變異、30 條選定 CFG walks、164 條 edge witnesses，以及 327,680 組乘法／進位案例。一般及 `-O` 模式均須精確重播 ledger；所有 guards 不依賴 Python assert。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_comparator_tail_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_comparator_tail_static.py
```

接續需完整核對 `640d8/641c2` generator，並將既有 timer／lookup／算術 helper 證據串接為更完整的返回與保存合約；實際 installed provider、global writers、alias、生命週期、控制欄位效果與事件送達仍未證明。
