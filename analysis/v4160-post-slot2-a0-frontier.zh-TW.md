# 索引 2 回呼之後：取消值是否控制派送？

起點是 V1.31 參考程式搬移後的 `0x20000820`，假設進入時 a0 仍為 6。以 Xwchc 解讀壓縮載入、正常記憶體存取；下列位址縮寫 `0820` 表示 `0x20000820`。

* 掃描使用 `0x2000319c` 的索引、下一個 byte 的計數，以及從 `0x200031e4` 取出的 pending 表。`0840` 先讀半字，`0842` 用它判空；`0848` 比較重新讀出的索引與計數。兩處都不讀 a0。空項會令索引加一並取低 8 位，不能把讀表說成先做界限檢查。
* **派送分支：首次碰 a0 是 `08ee` 的覆寫。** `08e8` 把 pending 半字讀入 a1，`08ea` 清該半字，`08ee` 再從 `0x2000319c` 載入 a0。所以 `090a` 的處理函式接到的是新讀出的任務索引，不是取消碼；即使兩個值剛好都是 6，來源仍不同。
* **不派送的分支：並非總會覆寫。** 在 `084c` 清索引後，若直接走 `0862` 且 `[0x200031e0]` 為零，`094e..095e` 可還原並返回，完全沒用 a0。若該槽非零，則 `0872` 先呼叫 `0x200004fa`；另有 `096e/0972` 先呼叫 `0x63dd0` 的分支。這兩個呼叫邊界前都不讀寫 a0，不能據此宣稱其內部不讀它。以上不是裝置的執行次序或可達性證明。

重現：傳入 V1.31 carrier。檢查選路指令窗，從搬移位址解碼三個重要轉移；再依指令長度核算起點至首次接觸 a0、首次子呼叫或返回的控制流邊界。回圈以已訪問 PC 截斷；這是靜態路徑，不是終止性或分支可行性測試。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok:raise ValueError('post-slot2 evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def check(p,h):
    v=bytes.fromhex(h);ck(b[0x270+p:0x270+p+len(v)]==v)
check(0x820,'37340020b73900209307c41903a7491e9033130ac4198347c41993961700ba969622c9ca8347c41963eec708230e041837340020930744519c371304445163910710b737002083a7071ef5c3dc402328fa006131')
check(0x8d4,'850793f7f70f230ef418e3ecc7f48db786073e970e23231007000345c419')
check(0x94e,'f2406244d2444249b249224a924a056182807c3093f7f70fe39e07eea3040400973006e0e7802046')
def w(p):return int.from_bytes(b[0x270+p:0x274+p],'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
def cj(p):
    x=w(p);d=sum((x>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));return p+sx(d,12)
ck(cj(0x872)==0x4fa and cj(0x8e2)==0x844 and (0x2000096e+(w(0x96e)&0xfffff000)+sx(w(0x972)>>20,12))&0xffffffff==0x63dd0)
seen=set();stop=set();todo=[0x820]
while todo:
    p=todo.pop()
    if p in seen:continue
    seen.add(p)
    if p in (0x8ee,0x95e,0x872,0x972):stop.add(p);continue
    x=w(p);h=x&65535;n=p+(4 if x&3==3 else 2);q=h&0xe003
    if x&127==99:
        d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;todo.append(p+sx(d,13))
    elif q in (0xc001,0xe001):
        d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5;todo.append(p+sx(d,9))
    elif q==0xa001:n=cj(p)
    ck(0x820<=n<=0x972);todo.append(n)
ck(stop=={0x8ee,0x95e,0x872,0x972});print('PASS: four static endpoints: cursor overwrite, untouched return, two calls')
```
