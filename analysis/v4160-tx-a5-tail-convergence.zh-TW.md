# TX 收尾：a5 在哪裡重新一致？

以原 BIN 和兩份實際連結的 selected-spans 為輸入，身分同[逐指令對照](v4160-tx-reordered-instructions.zh-TW.md)。以下從已寫完 checksum、總長、游標的狀態說明；不把每條指令之後的狀態視為等價。

|原版 / 候選 PC|正常執行時的結果|
|---|---|
|8b3a、8b3e / 8b54、8b56|令 X 為此處原先的 a2。原版先寫 a5=gp+148，再令 a2=X+a5；候選只改 a2，先加 gp 再加 148。兩版的 a2 同為 `(X+gp+148) mod 2^32`，a5 尚可能不同。|
|8b40 / 8b5a|`lw s0,24(sp)` 從相同位址讀相同字，不讀 a5。若此讀取不成功，不能沿用後續結論。|
|8b42 / 8b5c|`lui a5,0x40` 不讀舊值，兩邊 a5 都變成 `0x40000`。|
|8b46–8b50 / 8b60–8b6a|依序讀 `t1=word[0x40050]`、`a0=byte[a2]`，sp 加 32，以 `jr t1` 尾跳到 `t1 & ~1`，不寫 ra，不再寫資料記憶體。|

**從 checksum store 前起做差分**：直接將原 BIN `0x8b14` 與 C、C++ 連結候選 `0x8b2e` 起的機碼交給相同的有限指令解譯器，不以差異清單合成候選。取 bank 0/1、長度 0..1039、相同入口暫存器與合成 RAM（sp=0x2000ff80、gp=0x20004000）。每份候選 2080 組；正常尾跳的目標、32 個整數暫存器、模型內整份資料記憶體，以及 10 筆有序讀寫（含寬度與值）皆一致。10 筆為 checksum 寫入、4 筆堆疊還原、2 筆描述元寫入、s0 還原、服務槽與 task ID 讀取。將候選最後的 s0 還原替換成 s1 還原，在最後一組樣本被檢出。

這驗的是正常完成的收尾，不是整個函式、服務執行或異常時中間狀態。原 BIN 未變，沒有連線設備。可獨立在上篇已固定 hash 的輸入上核對最後 24 bytes（`b`、`c` 同上篇）；兩個位址在第一個連續 span：

```python
common=bytes.fromhex('6244 b7070400 03a30705 03450600 0561 0283')
if b[0xb3a:0xb52]!=bytes.fromhex('93874109 3e96')+common: raise ValueError('original tail')
if c[0xb54:0xb6c]!=bytes.fromhex('0e96 13064609')+common: raise ValueError('candidate tail')
print('PASS: 18 identical bytes from s0 restore through tail jump')
```
