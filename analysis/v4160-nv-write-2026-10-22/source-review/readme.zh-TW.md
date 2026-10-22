# 原始 NV 寫入與 timer 來源契約

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本範圍只分析 ID2966 V4.1.60 原始韌體的六段已閉合來源 CFG，協助核對新的 C/C++ 實作。沒有執行原始指令、CPU／ISA／ESIL、native／HOST、MMIO 或硬體，沒有產生 BIN，也沒有網路操作。這不是完整韌體或可燒錄相容性的證明。

原始檔 SHA-256：`0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，76800 位元組。分析映射為 VA `0x8000`，檔案位移為 `VA-0x8000`，沒有補洞。

|來源|半開區間|位元組|列數|
|---|---|---:|---:|
|寫入 wrapper|197BE..197F0|50|20|
|timer|19764..1979A|54|22|
|unlock|18E98..18EB6|30|10|
|lock|18EB6..18EC4|14|6|
|erase|18EC4..18EF2|46|19|
|program|18EF2..18F56|100|38|
|合計||294|115|

`ledger.json` 保留每列原始 bytes、位址及所有解碼欄位。`r2-static.json` 是另行對這些原始範圍執行的靜態 r2 欄位交叉核對，未保留或執行 ESIL。CFG 的 calls 只沿正常返回續接；所有五個直接依賴都是 leaf。保留完整 RET、分支回邊及每個 body 的實際寫入 GPR，不把下一個符號盲目當作函式大小。

## 寫入 wrapper

入口 A0 是目的位址 D，入口 A2 是來源 S。入口 A1 在覆寫前沒有讀取，不能稱為可變長度。197BE 保留整個 32-byte frame；197C0／197C2／197C4 分別以 word 寫入 F+28 的 RA、F+24 的 S0、F+12 的 A2，其中 F=u32(entrySP-32)。剩餘 frame 位元組沒有 wrapper 的明示 store。S0 暫存 D。

五個 linked calls 順序固定：

1. 197C8→18E98 unlock，A0=D。
2. 197CE→18EC4 erase，A0=D；leaf 內以 `D & 0xFFFFFF00` 對齊。
3. 197D8→18EF2 program，A0=D，A1=197D2 對 F+12 的新 word read，A2 同值；program 在使用前把 A2 設為 256。
4. 197DC→18EB6 lock，A0=對齊 D，A1=來源，A2=256；沒有先重設這些暫存器。
5. 197E2→19764 timer，A0=1，A1=來源，A2=256。

197E6／197E8 新讀 F+28／F+24 恢復 RA／S0；197EA 設 A0=0，197EC 釋放整個 frame。A0=0 不表示檢查到硬體成功；原始 wrapper 沒有成功狀態判斷。

若所有存取及輪詢正常完成，且沒有破壞 frame／來源／目的／MMIO 的 alias 或外部修改，出口 A1=S、A2=新讀 GP+382 byte、A3=0、A4=timer 最後新讀 CTRL 清 bit0、A5=E000F000、A6=最後一個來源 word。SP、RA、S0 恢復入口值；其他 S、GP、TP、T、A7 沒有這些 body 的明示寫入。若 alias 破壞保存位置，僅能說明恢復了該位置的新讀值，不能無條件宣稱入口值被保留。

## Timer 的 12 項最少存取

`effects.json` 提供機器可讀的順序、PC、寬度、公式及各 leaf 的出口暫存器。R8／R32 一律是新讀，W32 一律為完整 word。

1. 19768：R32(E000F004)。
2. 1976E：W32(E000F004, 上次讀值 & FFFFFFFE)。
3. 19770：R8(u32(GP+382))，零擴展。
4. 19778：W32(E000F010, u32(byte × 完整入口 A0))。
5. 1977A：W32(E000F014, 0)，並非乘積高 word。
6. 1977C：新讀 R32(E000F000)。
7. 19782：W32(E000F000, 該讀值 | 10)。
8. 19784：再新讀 R32(E000F000)，不能沿用上次值。
9. 1978A：W32(E000F000, 該讀值 | 21)。
10. 1978C：反覆新讀 R32(E000F004)，19790 在 bit0=0 時回跳，直到觀察到 bit0=1。
11. 19792：再新讀 R32(E000F000)。
12. 19796：W32(E000F000, 該讀值 & FFFFFFFE)。

上列暫存器地址與 mask 使用十六進位。總存取數是 `11 + poll reads`，正常返回至少 12 次。乘法用完整 32-bit A0，結果取低 32-bit；沒有把 A0 截成 byte，也沒有把 product 當 bool。A0／A1 未被 timer 寫入。正常返回 A2=乘積低 word、A3=0、A4=最後 CTRL & FFFFFFFE、A5=E000F000。沒有 SP frame、call 或其他 GPR 寫入。

這個等待條件與 Flash 等待清除位元不同。沒有 timeout，無法證明一定終止；本函式也不初始化 GP+382，沒有來源證據可以把參數命名為毫秒。MMIO 可以在各次新讀之間改變，並未假設穩定值。

## 四個 Flash leaf

unlock 按順序把 45670123、CDEF89AB 寫入 40022004，再依相同順序寫入 40022024。lock 新讀 40022010 後 OR 8000 寫回。

erase 新讀 CTRL 後 OR 20000，寫對齊目的位址到 base+20，再新讀 CTRL 後 OR 40。其 base+12 bit0 輪詢直到清除，最後新讀 CTRL 後 AND FFFDFFFF。program 新讀 CTRL 後 OR 10000；依序等待 base+12 的 bit0、bit1 清除，再以 offset 0、4、…、252 交錯執行新來源 word read、目的 word write、bit1 清除輪詢。最後新讀 CTRL 後 OR 200000，等 bit0 清除，再新讀 CTRL 後 AND FFFEFFFF。program 沒有預先快取來源；原始 A0 保持對齊基底，A1 保持來源，A2 結束為 256。

這些數值契約來自原始 operand，沒有借用 SDK prototype 或推定板上晶片身份。四個 leaf 的完整出口 GPR 和 effects 由 `effects.json` 列出。全部忙等都沒有 timeout，也沒有檢查成為成功旗標。

## 重跑與限制

```sh
python3 -B check.py --project-root ROOT
python3 -B check.py --project-root ROOT --firmware /absolute/ID-2966-V4.1.60-decoded.bin
./check.sh --project-root ROOT --firmware /absolute/ID-2966-V4.1.60-decoded.bin
```

Windows 可直接使用已安裝的 Python 執行 check.py。預設只核對封存來源 metadata，回報實際原始檔讀取 bytes／rows 為 0。只有明確提供 `--firmware` 才重新核對實檔 SHA、294 bytes／115 rows 及七項 raw operand 控制：frame 保存位移、direct call target、GP byte 位移、MUL 來源、零 high-word store 來源、poll 分支方向、固定 program 長度。控制會翻轉真實來源的一個 bit，只接受預定欄位改變且其他欄位相同的解碼，不生成新 opcode，也不執行修改內容。

`mode-controls.json` 保留模式與錯誤實檔控制；`dependency-availability.json` 記錄封存前 W／D／P 的既有相依閉包均可核對。新 checker 只讀；封存後重跑前後 member hashes 一致。check.sh 未在這台機器重試曾拒絕的 Git Bash；Python 入口已驗證。

沿用而不修改 `callback-frontiers-2026-10-22/binding-review`，seal SHA-256 `a1d0dc4d3e8767e8dbd959235133779650f1da649c2d3f8ddbb38662addea9a7`，包含其已封存 decoder／encoding 來源及必要前置證據。`seal.json` 釘住本次所有 member。尚未證明實際硬體身份、Flash 所有權、硬體寫入成功、whole OTA、fault equivalence 或新的 native 全部 ABI；這些不能由本機靜態來源檢查推定。
