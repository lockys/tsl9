# 8 個取消尾跳：誰接到返回值？

`jal x0,0x90b0` 不改 ra；正常返回時不是從尾跳後的 PC 繼續。下表按既有來源分塊辨認所屬入口，再以原 APP 掃描指向這些入口的 JAL / RV32C C.J(AL) 編碼。它不是間接呼叫的完整清單。

|取消尾跳／所屬入口|上層證據|
|---|---|
|a450／a3cc、fb5a／fb1e、fb9e／fb5e|未找到直接跳到這三個入口的編碼。a460、fb40、fb80 分別把自己的入口算入 a0；形成函式地址不是當場呼叫。若由既有表派送器 9058 呼叫，返回到 905a 即覆寫 a0。|
|a5fe／a4ee|三個有連結的呼叫。a88a 返回後呼叫 8202，首條 AUIPC 即覆寫 a0；a8c0、a8e4 返回後直接把 a0 設為 106、107。|
|b294／b254|b4d0 返回到 b4d2，測的是 s1；若零則直接還原返回，**取消狀態能保留到再上一層**，非零則 b50e 用 s0 覆寫 a0。f11a 返回後直接設 a0=100；da2a 是另一尾跳，不在 da2e 接結果。這是第二次取消的結果，不是 b284 第一次的。|
|d686／d668|e666、161bc 都帶 a0=1 尾跳，入口依此走排程而非取消。e66c 帶 a0=0 呼叫才走取消，返回到 e670 再跳 e568，第一個判斷測 s0；尚未判定後續所有分支。|
|1062c／1061c|10714 呼叫後在 10722 以 AUIPC 覆寫 a0；1738e 為尾跳，須再往上追。|
|10748／1070a|五個有連結的呼叫。其中 12a74、12aa6 正常返回後先從 sp+12 重讀 a0 才判斷；12b2c、147fc、14930 尚不可只憑呼叫點判定最後用途。|

重現：傳入原 decoded APP。檢查八個尾跳、上層 16 個直接編碼及混合返回路徑；正常的堆疊／返回與成功讀寫是條件，不是實機證據。

```python
import sys
from pathlib import Path
from hashlib import sha256
b=Path(sys.argv[1]).read_bytes(); base=32768
def ck(x):
    if not x: raise ValueError('tail evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
e={0xa3cc:[],0xa4ee:[0xa88a,0xa8c0,0xa8e4],0xb254:[0xb4d0,-0xda2a,0xf11a],0xd668:[-0xe666,0xe66c,-0x161bc],0xfb1e:[],0xfb5e:[],0x1061c:[0x10714,-0x1738e],0x1070a:[0x12a74,0x12aa6,0x12b2c,0x147fc,0x14930]}; found={k:[] for k in e};tails=[]
for i in range(0,len(b)-1,2):
    p=base+i;x=int.from_bytes(b[i:i+4],'little')
    if x&127==111 and i+4<=len(b):
        d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;t=p+(d^1048576)-1048576;r=x>>7&31
    elif x&0xe003 in (0x2001,0xa001):
        d=sum((x>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));t=p+(d^2048)-2048;r=int(x&0xe003==0x2001)
    else:continue
    if t in e:ck(r in (0,1));found[t].append(p if r else -p)
    if t==0x90b0 and not r:tails.append(p)
ck(found==e and tails==[0xa450,0xa5fe,0xb294,0xd686,0xfb5a,0xfb9e,0x1062c,0x10748])
for p,h in [(0xb4d2,'95ecb24022449244024941018280'),(0xb50e,'2285'),(0xd668,'19c9'),(0xe662,'05454101'),(0x161b8,'05454101'),(0xe66a,'0145'),(0x9058,'82960545')]:
    v=bytes.fromhex(h);ck(b[p-base:p-base+len(v)]==v)
print('PASS: 8 cancellation tails, 12 upper calls and 4 upper tails')
```
