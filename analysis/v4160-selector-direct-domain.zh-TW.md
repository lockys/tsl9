# 0x12b24 的直接呼叫：已追到的參數與返回值

在 v4.1.60 APP 全部半字位置掃 JAL 及標準 RV32C 的 C.J/C.JAL，到 `0x12b24` 只有兩個命中，均為 `jal ra`。逐段反組譯所得：

|呼叫點|傳入 a0|正常返回後|
|---|---|---|
|`0x16f9a`|前一條指令設 0|`xori a0,s0,1` 覆寫返回值|
|`0x1077a`|`0x10766` 設 `s0 & 255`，至呼叫前只有取址及寫入|`0x1077e` 測完整 s0，不測 a0；非零到 `0x10788` 用 AUIPC 覆寫 a0，零到 `0x10794` 設 a0=0|

追 `0x1074c`：`0x10752` 保存入口值到 s0。`0x107c2/0x147be/0x154a2` 三條直接路徑傳 0；`0x1080c` 的門檻命中路徑傳 s1。後一路在 `0x107d4` 取入口 a2；已追到的 `0x10bbe` 兩條前綴分別設 5、1，`0x10bda` 前設 2。假設相關子呼叫正常返回、保全活躍的 s0/s1 及保存槽，這些路徑給出的候選集合為 **{0,1,2,5}**，沒有大於 6 的例子。不代表四值都曾在實機出現，也不排除間接入口、從片段中間進入或其他未建模路徑。即使另外給 `0x1077a` 一個大於 6 的低位元組，[前一階段](v4160-selector-cancel-return.zh-TW.md)所示的取消返回碼在這一層仍被覆寫。

重播：repo 根目錄、Python 3，從原 BIN 掃描而非從符號清單推算。這是直接跳轉編碼盤點，不是全域控制流證明。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('direct caller mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
hits={0x12b24:[],0x1074c:[],0x107c6:[]}
for i in range(0,len(b)-1,2):
    w=int.from_bytes(b[i:i+4],'little'); h=w&65535
    if w&127==111 and i+4<=len(b):
        d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1; sign=1<<20; rd=w>>7&31
    elif h&0xe003 in (0x2001,0xa001):
        d=sum((h>>s&1)<<k for s,k in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11))); sign=2048; rd=int(h>>13==1)
    else: continue
    p=32768+i; dest=p+(d^sign)-sign
    if dest in hits: hits[dest].append((p,rd))
ck(hits=={0x12b24:[(0x1077a,1),(0x16f9a,1)],0x1074c:[(0x107c2,0),(0x1080c,0),(0x147be,1),(0x154a2,0)],0x107c6:[(0x10bbe,0),(0x10bda,1)]})
for p,h in [(0x10752,'2a84'),(0x10766,'1375f40f97c7ff1f2385078497c7ff1fa381a784'),(0x1077e,'19c8'),(0x10788,'1795ffff'),(0x10794,'0145'),(0x16f98,'0145'),(0x16f9e,'13451400'),(0x107c0,'0145'),(0x147bc,'0145'),(0x1549e,'01454101'),(0x10806,'2685d2440561'),(0x107d4,'b284'),(0x10ba4,'1546'),(0x10bb6,'0546'),(0x10bd0,'0946')]:
    v=bytes.fromhex(h); ck(b[p-32768:p-32768+len(v)]==v)
print('PASS: 2 + 4 + 2 direct edges; known argument prefixes and both return consumers')
```
