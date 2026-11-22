# ID 820 與 1001：校驗通過後的記錄變換

沿前一階段的兩個成功尾跳，以 P 表示該次傳入的記錄。下表是 APP 指令直接可見的操作，不含子呼叫的額外副作用，也不賦予欄位未證實的硬體名稱。

| |820：`0xf860`|1001：`0xfba2`|
|---|---|---|
|起始判定|取 `LHU[P+2]` 的 bit 13（小端即 `P[3]` bit 5）。與 `gp+276` 不同時把該位寫到 `gp+276`、`gp+277`，呼叫兩個 helper，之後重新讀這兩個狀態，不假定仍相等。|先看 `gp+290`。值 1 時把 `P[3]` 低兩位調成 1；值 2 且低兩位非零時先呼叫 `0x8202`，返回零才清低兩位。|
|條件式記錄寫入|`P[3]` bit 5、`P[5]` 的查表合成、`P[6]` 的旗標及高兩位。|`P[3]` 的多組位元、`P[4]` bits 3–4、`P[5]` bit 6、`P[6]` bit 0。操作由設定及 `gp+288..290` 等即時值選擇，不是每次全寫。|
|額外狀態|`gp+278/279` 影響 `P[6]` 的低位，`gp+280` 參與高位選擇。|讀到 `gp+288==2` 會寫 3 並請求 `0x9124(0xfd3e,0,20,0)`；讀到 3 則清零。`gp+289==2` 也會清該狀態。|

**共同出口**：兩函式都有直接返回、不轉交的分支。若進入更新尾段，兩者都把 `P[9]` 加 `0x10`（低四位保留，高四位模 16 遞增），取 `n=P[2]`，呼叫 `0xed00(P,7)`，把返回值低位元組寫至 `P+n+2`，再尾跳 `0x12a08(P)`。這不同於先前驗證固定讀 `P[10]`；只有 `n==8` 時兩個偏移才相等。

**1001 的差異不是只有欄位不同**：`gp+288==3` 的路徑與 `gp+289==2` 的路徑各能在共同尾段前多加一次 `0x10`。若兩條依序成立且狀態、記錄與棧互不重疊，一次處理可見三次 `P[9]` 更新，例如 `0xe7 → 0xf7 → 0x07 → 0x17`（不含後續校驗寫入）。不能把每次經過此函式都當成只加一次，更不能以校驗通過推論一定有轉交。

離線重播（repo 根目錄）：盤點原始區間半字邊界上以 s0 為基底的 SB 編碼；核對校驗呼叫、尾跳及兩條額外加法區塊，逐值比較兩種加法。這是指令及算式核對，不是完整執行或真機觀測。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('mode1 transform mismatch')
def w(p): return int.from_bytes(b[p-32768:p-32768+4],'little')
def pin(p,h):
    v=bytes.fromhex(h); ck(b[p-32768:p-32768+len(v)]==v)
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for lo,hi,expected in [(0xf860,0xf97c,[3,5,6,6,9]),(0xfba2,0xfd3e,[4,6,3,3,3,3,3,9,5,9,5,9])]:
    off=[]
    for p in range(lo,hi,2):
        v=w(p)
        if v&0xff07f==0x40023: off.append((v>>25<<5)|(v>>7&31))
    ck(off==expected)
for p,rd,t in [(0xf934,1,0xed00),(0xf948,0,0x12a08),(0xfd02,1,0xed00),(0xfd16,0,0x12a08),(0xfcb2,1,0x9124)]:
    v=w(p); d=(v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1
    ck(v&4095==111+128*rd and p+(d^1048576)-1048576==t)
for p in (0xfcca,0xfcf0,0xfd2e): pin(p,'13f7070f4107bd8bd98fa304f400')
for p in (0xf938,0xfd06): pin(p,'a294a381a4002285')
pin(0xf92a,'c107a304f400fd149d45'); pin(0xfcfe,'fd149d45')
for x in range(256):
    y=x
    for k in (1,2,3):
        y=((((y&240)+16)|(y&15))&255); ck(y==(x+16*k)&255)
ck([n for n in range(256) if n+2==10]==[8])
print('PASS: two store inventories, five call/jump targets, 768 nibble increments, 256 output offsets')
```
