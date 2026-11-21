# 節點入口表：啟動清零與四條填表路徑

在 V1.31 參考 resident，正常跑完[啟動清零](v4160-capacity-wide-init.zh-TW.md)時，兩張三欄表均為零：從 `0x20002ef8` 起算，`0x20003390` 佔第 294–296 個 word（從零計），`0x200033a0` 佔 298–300。這證明的是清零迴圈結束時的值，而非首次讀取時仍為零。

對 APP 與參考 resident 每個半字對齊位置掃描 32-bit JAL 編碼，指向[填表者](v4160-node-writer-entry-tables.zh-TW.md) `0x50368` 的只有 `0x50418`；指向其呼叫者 `0x50412` 的有四處，均在 resident。按各自入口正常順序：

|參考槽 → 入口|先呼叫|到 `0x50412` 的呼叫點|與首次角色讀取的關係|
|---|---|---|---|
|`40188 → 6dca6`|`55bde`|`6dcea`|此入口先進入判斷，返回後才填表。|
|`40190 → 6dc36`|`60856`|`6dc7a`|另一條填表路徑；尚無它早於首次讀取的執行證據。|
|`401a0 → 6dd16`|`61b1c → 55bde`|`6dd5a`|APP 在 `8eb6` 呼叫的路徑；這一次晚於讀取。|
|`401ac → 6dd86`|`5a004`|`6dde0`|APP 在 `8ebc` 才呼叫；且此入口的分支可略過填表。|

因此不能以四個槽的排列推論執行次序。這是限定編碼的離線盤點，不排除間接跳轉、其他 store 或區塊複製；未證裝置 ROM。重現：參數依序為 decoded APP、V1.31 carrier。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=[Path(s).read_bytes() for s in sys.argv[1:]]
def ck(v):
    if not v: raise ValueError('entry table startup evidence mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(b[0x292:0x2b0].hex()=='b737002037370020938787ef130747616373f700828023a007009107d5bf')
starts=list(range(0x20002ef8,0x20003618,4));ck(len(starts)==456 and [starts.index(x) for x in (0x20003390,0x20003394,0x20003398,0x200033a0,0x200033a4,0x200033a8)]==[294,295,296,298,299,300])
def jal(x,p):
    j=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;return p+(j^1048576)-1048576
hits=[]
for blob,base in [(a,0x8000),(b,0x40000)]:
    for i in range(0,len(blob)-3,2):
        x=int.from_bytes(blob[i:i+4],'little');p=base+i
        if x&127==111 and (t:=jal(x,p)) in (0x50368,0x50412): hits.append((base,p,t,x>>7&31))
ck(hits==[(0x40000,p,t,1) for p,t in [(0x50418,0x50368),(0x6dc7a,0x50412),(0x6dcea,0x50412),(0x6dd5a,0x50412),(0x6dde0,0x50412)]])
for slot,e,t in [(0x188,0x6dca6,0x55bde),(0x190,0x6dc36,0x60856),(0x1a0,0x6dd16,0x61b1c),(0x1ac,0x6dd86,0x5a004)]:
    ck(int.from_bytes(b[slot:slot+4],'little')==e);p=e+4;x=int.from_bytes(b[p-0x40000:p-0x40000+4],'little');ck(x&4095==239 and jal(x,p)==t)
ck(a[0xeb2:0xebe].hex()=='8327041a82978327c41a8297');print('PASS: 6 cleared words, 5 direct JAL sites, 4 role slots, APP slot order')
```
