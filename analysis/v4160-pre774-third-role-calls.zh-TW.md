# 774 之前：第三個角色入口內的 JALR 不是派送器

原 APP 的三次角色呼叫在參數 774 前，依序從 `s0+0x1a0/+0x1ac/+0x1c0` 讀目標。在 `s0=0x40000` 且服務表與 V1.31 相同的條件下，第三個入口是 `0x66056`。按指令邊界走到 `0x66096` 的普通返回，可區分三個呼叫：

|呼叫點|目的|作用|
|---|---|---|
|`0x6605c`|`0x64298`|直接進入初始化子程序，內部效果另計|
|`0x6606e/72`|`0x2000039c`|AUIPC/JALR 的基址來自 PC，不是從 RAM 第零槽讀出。參數是 `(0x20003560,0,36)`，對應參考 fill|
|`0x66084`|`0x43c4e`|傳入 `0x65920` 登記處理函式，不是呼叫它|

因此這三個呼叫點都不會直接執行 `0x200007d0`。尤其不能把 `jalr 814(ra)` 單獨視為尚未解析的回呼。這不是「初始化不可能派送」的證明：例如 `0x64298` 的內層及其他兩個角色路徑仍須分開處理，參考 ROM 也不等同實機。

複核（repo 根目錄，參數為原 APP、V1.31 主區；`check_v4160_role_init_args.check` 核對 APP 身分、槽及先後）：

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v4160_role_init_args import check
from check_v131_descriptor_edges import edges
a,r=(Path(p).read_bytes() for p in sys.argv[1:]); check(a)
def ck(x):
    if not x: raise ValueError('third role mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(int.from_bytes(r[0x1c0:0x1c4],'little')==0x66056)
pc=0x66056; calls=[]
while pc<0x66098:
    i=pc-0x40000; h=int.from_bytes(r[i:i+2],'little'); n=4 if h&3==3 else 2
    if (n==4 and r[i]&127 in (103,111)) or (n==2 and h&0xf07f in (0x9002,0x8002)):
        calls.append(pc)
    pc+=n
ck(calls==[0x6605c,0x66072,0x66084,0x66096] and r[0x26096:0x26098]==bytes.fromhex('8280'))
for pc,t,n in [(0x6605c,0x64298,4),(0x6606e,0x2000039c,8),(0x66084,0x43c4e,4)]:
    ck(edges(r[pc-0x40000:pc-0x40000+n],pc,t)==[(hex(pc),'JAL' if n==4 else 'AUIPC/JALR',1)])
ck(r[0x26060:0x2606e].hex()=='3734002013050456130640028145')
ck(r[0x26076:0x26080].hex()=='37650600fd5713050592' and 0x66000-1760==0x65920)
print('PASS: 3 resolved calls, 1 return; no scheduler target at these sites')
```
