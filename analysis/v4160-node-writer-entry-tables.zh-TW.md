# 兩個節點寫入者的上游：先寫函式表，沒有當場呼叫

V1.31 參考映像中，先前的[兩個節點寫入者](v4160-list-flag-node-bases.zh-TW.md)各有一條經過 RAM 函式表的候選入口：

|函式指標存放處|值（入口）|函式內的呼叫 → 尾跳 → 呼叫|
|---|---|---|
|`0x200033a8`|`0x4f39e`|`0x4f40a → 0x5339a`，`0x533a2 → 0x67390`，`0x67394 → 0x6872e`|
|`0x20003398`|`0x515ee`|`0x5163a → 0x533a6`，`0x533a6 → 0x673a8`，`0x673b0 → 0x68844`|

兩個入口都是三欄表的第三個 word。`0x50368` 先清三個 word，再填六欄、返回，沒有呼叫其中任何一欄。已辨認角色初始化路徑在 `0x6dd1a → 0x61b1c → 0x55bde` 先進入首次判斷；正常返回後，第四次登記才走 `0x6dd5a → 0x50412 → 0x50368`。因此**這一次填表太晚**，不能作為首次 `0x55be2` 讀取前已執行兩個節點寫入者的依據。尚未排除其他入口、其他填表者、非同步呼叫或不同 resident；不是實機順序證明。

重現：將參考 carrier 路徑作為下段 Python 的第一個參數。僅解碼填表函式所用指令和十條指定直接跳轉，不解譯整個呼叫鏈。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('entry table evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p): return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
for p,t,r in [(0x6dd1a,0x61b1c,1),(0x61b20,0x55bde,1),(0x6dd5a,0x50412,1),(0x50418,0x50368,1),(0x4f40a,0x5339a,1),(0x533a2,0x67390,0),(0x67394,0x6872e,1),(0x5163a,0x533a6,1),(0x533a6,0x673a8,0),(0x673b0,0x68844,1)]:
    x=w(p);d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==111+128*r and p+(d^0x100000)-0x100000==t)
p=0x50368;reg={0:0};stores=[]
while p<0x503d0:
    x=w(p);rd=x>>7&31;rs=x>>15&31;h=x&65535
    if h&3!=3:
        ck(h&0xe003==0xc000);off=(h>>10&7)*8+(h>>6&1)*4+(h>>5&1)*64;stores.append((reg[8+(h>>7&7)]+off,reg[8+(h>>2&7)]));p+=2;continue
    if x&127==55: reg[rd]=x&0xfffff000
    elif x&0x707f==19: reg[rd]=reg[rs]+((x>>20^2048)-2048)
    elif x&0x707f==0x2023: stores.append((reg[rs]+(((x>>25<<5|rd)^2048)-2048),reg[x>>20&31]))
    else: raise ValueError(hex(p))
    p+=4
ck(p==0x503d0 and w(p)&65535==0x8082);ck(stores==[(0x2000339c,0),(0x2000338c,0),(0x20003388,0),(0x200033a0,0x5091a),(0x200033a4,0x50668),(0x200033a8,0x4f39e),(0x20003390,0x517a0),(0x20003394,0x5134e),(0x20003398,0x515ee)])
print('PASS: 10 direct edges; 3 clears then 6 function pointers; ret')
```
