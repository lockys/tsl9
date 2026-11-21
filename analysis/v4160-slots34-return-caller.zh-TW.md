# 槽 3、4 原樣返回後，呼叫者是否使用取消碼？

在 V1.31 參考映射中，槽 3 從 `0x20000816` 載入，槽 4 從 `0x200008d0` 載入並跳到同一個 `0x20000818: c.jalr a5`。兩者的返回位址都是 **`0x2000081a`**。假設所登記目標正常原樣返回、保存 s0 與返回位址，這裡不會比較 a0、把它存入 RAM，或先清掉它。

| 實際重新讀取的槽 2 | 呼叫者的行為 |
|---|---|
| `[s0+8] == 0` | `0x2000081c` 依 **a5** 跳到 `0x20000820`，a0 原值進入 pending 掃描。 |
| `[s0+8] != 0` | `0x2000081e` 呼叫剛載入的指標（目標最低位清零），a0 原值傳給它，返回位址也是 `0x20000820`。此後 a0 是槽 2 的返回狀態，不能一概認為仍為 6。 |

若 s0 保存的是已設好的表基址 `0x200031c8`，上述讀取來自 `0x200031d0`；不是重用槽 3/4 的 a5，也不是按哪個槽剛返回而選路。對[已知槽 2 候選](v4160-slot2-clock-first-use.zh-TW.md)，可原樣返回，亦可由已登記的時鐘覆寫 a0；若指標不同，不能替未知回呼作結論。[pending 掃描](v4160-post-slot2-a0-frontier.zh-TW.md)在派送時以任務索引覆寫 a0，空閒分支則不一定覆寫。這是特定呼叫點的離線結論，非所有呼叫者或實機證明。

重現：將 V1.31 carrier 路徑作為參數。小解譯器只執行列出的 C.LW、C.J、C.JALR、C.BEQZ、C.JR；從兩個候選的實際 `ret` 開始模擬返回，跳過其函式本體，故「原樣返回」是前提。對四種槽值與全部 256 個 byte 逐一核對所讀地址、連結位址及 a0，包括相同取消碼但不同目標的情形。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes();base=0x20000000;T=0x200031c8
def ck(ok):
    if not ok:raise ValueError('slot return mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def step(p,r,mem,reads):
    i=p-base+0x270 if p>=base else p-0x40000;h=int.from_bytes(b[i:i+2],'little');q=h&3;f=h>>13;u=8+(h>>7&7);v=8+(h>>2&7)
    if (q,f)==(0,2):
        k=((h>>5&1)<<6)|((h>>10&7)<<3)|((h>>6&1)<<2);a=r[u]+k;reads.append(a);r[v]=mem[a]
    elif (q,f)==(1,5):return p+sx(sum((h>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11))),12)
    elif (q,f)==(1,6):
        d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
        if not r[u]:return p+sx(d,9)
    elif h in (0x9782,0x8082):
        t=r[h>>7&31]&~1
        if h&4096:r[1]=p+2
        return t
    else:raise ValueError(hex(h))
    return p+2
for k,entry,ret in [(3,0x60516,0x60752),(4,0x58c52,0x58e78)]:
    for ptr in (0,0x20002ca8,0x20002ca9,0x12345678):
        for val in range(256):
            r=[0]*32;r[8]=T;r[10]=val;m={T+4*k:entry,T+8:ptr};reads=[]
            p=step(base+(0x816 if k==3 else 0x8d0),r,m,reads)
            if k==4:p=step(p,r,m,reads)
            ck(p==base+0x818 and step(p,r,m,reads)==entry and r[1]==base+0x81a)
            p=step(ret,r,m,reads);ck(p==base+0x81a);p=step(p,r,m,reads);ck(p==base+0x81c);p=step(p,r,m,reads)
            if ptr:ck(p==base+0x81e and step(p,r,m,reads)==ptr&~1 and r[1]==base+0x820)
            else:ck(p==base+0x820 and r[1]==base+0x81a)
            ck(r[10]==val and reads==[T+4*k,T+8])
print('PASS: 2048 cases; common return PC 0x2000081a; slot 2 reloaded; a0 unchanged at skip/call')
```
