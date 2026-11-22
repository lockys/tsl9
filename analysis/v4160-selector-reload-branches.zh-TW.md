# 讀回 selector 之後：0 是 14 筆周邊設定，1/2 才走事件取消

承接[三次查表](v4160-selector-three-lookups.zh-TW.md)。以下分類依 `0x12aaa` **實際讀回的完整 word**，不是依前一個函式的返回值。

|讀回值|本路徑提出的操作|
|---|---|
|0|尾跳 `0x129c4`。每輪在棧上重建一筆 20-byte 記錄交給 `0x18ba2`，記錄 `+10` 依序為 0..13、`+11=1`、`+16` 的 word 為 1，其餘為零。這是周邊設定迴圈，不是送出遮罩 1。|
|完整值 1、2|經 `0x16dac` 把兩個零 byte、長度 2、動作 0 傳給 `0x16cc4`。若中間服務正常返回並保持保存暫存器，六輪 `0x168de` 之後才到 `0x16858`，以 `gp+363` 的任務 ID **取消**遮罩 2、4（槽 `0x4005c`），不是新增定時器。|
|其他非零、低 byte 不為 1 或 2|`0x16db6` 直接跳到 `ret`，這個分支不提出事件請求。|

其他非零 word 若低 byte 恰為 1 或 2，只能說通過入口檢查，不能套用完整索引 1、2 的表項。也不能把本函式返回解釋為周邊已生效、取消成功或事件已執行。

檢查（repo 根目錄，Python）：解碼原 APP 的分流、直接呼叫目標及零分支棧上 store 的來源與位置，用非零初值重建每筆記錄。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('reload branch evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n],'little')
def jal(p,rd):
    w=u(p,4); ck(w&4095==111+128*rd); d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    return p+(d^1048576)-1048576
ck([jal(p,rd) for p,rd in [(0x12ab2,0),(0x12aba,0),(0x129f2,1),(0x16dc8,1),(0x16d7e,1),(0x16d92,1)]]==[0x129c4,0x16dac,0x18ba2,0x16cc4,0x168de,0x16858])
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
pin(0x12aaa,'324509e5'); pin(0x129d0,'014485490549b944'); pin(0x129de,'050468001374f40f'); pin(0x129f6,'e31194fe'); pin(0x16dac,'9307f5ff93f7f70f0547636ef700'); pin(0x16dbc,'6c008146094606ce23160100'); pin(0x16d82,'e31569fd'); pin(0x16d8e,'ce852285')
for j in range(14):
    m=bytearray([0xa5]*64); regs={0:0,8:j,18:1,19:1}
    for pc in (0x129d8,0x129da,0x129e6,0x129e8,0x129ec,0x129ee,0x129f0):
        h=u(pc,2)
        if h&3==2:
            ck(h>>13==6); d=(h>>9&15)*4+(h>>7&3)*64; v=regs[h>>2&31]; n=4
        else:
            w=u(pc,4); ck(w&0x000fffff==(2<<15|((w>>7&31)<<7)|35)); d=(w>>25)*32+(w>>7&31); v=regs[w>>20&31]; n=1
        m[d:d+n]=v.to_bytes(n,'little')
    ck(m[12:32]==bytes(10)+bytes([j,1])+bytes(4)+bytes([1,0,0,0]))
print('PASS: 6 direct transfers; 14 complete peripheral records')
```
