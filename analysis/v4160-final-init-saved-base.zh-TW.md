# 首次角色呼叫前：0x907a 的清零與登記是否碰到保存的 s0？

在[既有啟動堆疊推導](v4160-cfg60-init-stack.zh-TW.md)的條件下，`0x9008` 入口 SP 為 `0x20010000`，`9008 → 9250 → 8e88` 三個仍在用的 frame 共 64 bytes。`0x8eb0` 呼叫 `0x907a` 時 SP 是 `0x2000ffc0`。再減 16 後，`0x907c` 保存 s0、`0x90a6` 載回 s0，兩者都在 `0x2000ffb8..bb`；返回位址在 `0x2000ffbc..bf`。

* `0x9094` 的三個參數是 `(0x2000be08,0,180)`。若 V1.31 的 RAM 複製映射成立，槽 `0x40048` 的 `0x2000039c` 對應 carrier `0x4060c`。除了暫存及還原外設控制字 `0x4002420c`，它只逐 byte 清 `[0x2000be08,0x2000bebc)`，沒有自己的 stack store。
* `0x90a2` 經槽 `0x40080` 傳入 `0x901a`。候選 `0x43c4e` 在容量已滿時不寫 RAM、返回 255；成功時更新計數 byte `0x2000319d`，再寫函式指標至 `T+4*i`。若表基址仍為 `T=0x200047f4`，即使把所有 256 個 byte 索引都納入，寫入都在 `[0x200047f4,0x20004bf4)`。不需假設這次一定獲配 ID 4。
* APP 返回前另寫 `gp+166` 一個 byte；按名義 `gp=0x20004000` 是 `0x200040a6`。兩個 provider 沒有直接改寫 s0 或另呼叫 callback。

因此在上述映射、基址、SP 正確且存取成功、無外部干擾的條件下，這些寫入不會改動保存的 s0 或返回位址。若進入 `0x907a` 的 s0 是 `0x40000`，回到 `0x8eb2` 仍為該值，故下一條載入取的是 **`0x401a0` 而非 `0x40190`**。不把數值假設當成裝置 ROM 或實際 SP 的證明。

重現（依序提供 decoded APP 與 V1.31 carrier）：

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('final init write-set mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def app(p,n):return a[p-0x8000:p-0x8000+n]
def w(p):return int.from_bytes(app(p,4),'little')
def pair(p):return p+(w(p)&0xfffff000)+((w(p+4)>>20^2048)-2048)
ck(app(0x907a,54).hex()=='411122c4370404003c4406c61306400b8145173500201305c5d782978327040817050000130505f88297b24022442383a10a41018280');ck(app(0x8eb0,8).hex()=='e9228327041a8297')
ck(b[72:76].hex()=='9c030020' and b[128:132].hex()=='4e3c0400');ck(b[0x60c:0x63a].hex()=='374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7');ck(b[0x3c4e:0x3c7e].hex()=='373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf')
D=pair(0x908c);n=w(0x9086)>>20;ck((D,n,pair(0x909a))==(0x2000be08,180,0x901a));s=0x20010000-16-16-32-16;lo=s+8;hi=s+16;ck((lo,hi)==(0x2000ffb8,0x2000ffc0));writes=[(D,n),(0x4002420c,4),(0x2000319d,1),(0x200040a6,1)]+[(0x200047f4+4*i,4) for i in range(256)];ck(all(p+n<=lo or hi<=p for p,n in writes));print('PASS: 180-byte fill, peripheral word, counter, 256 table indices and APP result byte disjoint from saved s0/ra')
```
