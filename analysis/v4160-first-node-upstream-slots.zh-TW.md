# 兩條建節點路徑：登記不等於執行

接續[首次讀值與節點來源](v4160-first-node-callback-order.zh-TW.md)。以下順序只限 v4.1.60 APP 同步正常返回、槽綁定 V1.31 參考實作的路徑。

* **通往 `0x584a4`：已定位一次較晚的登記。** 第二角色經 `0x6dd8a → 0x5a004`，先呼叫 `0x60856`，再由 `0x5a00c` 呼叫 `0x58ef2`。後者把 `0x58c52` 存到 `0x200034f0`，隨即返回。它沒有執行這個回呼。該函式內有 `0x58d18 → 0x58498`，另一分支經 `0x58da2 → 0x588b4`，在 `0x5895e` 也可呼叫 `0x58498`。後者局部直落要求 s3=13 且 `0x585c8` 返回非零。兩者通往 `0x584a4`；但經這次登記才觸發的呼叫不可能早於第一角色讀值。不排除其他來源。
* **通往 `0x5c8c6`：發現另一個回呼槽，而非直接初始化呼叫。** `0x5c9b4` 函式內，`0x5cce4` 讀 `[s4+3]` 的 bit 0；為零即越過 `0x5ccee → 0x5c830`。後者另有多個判斷才到 `0x5c8c6`。`0x5cfa8`、`0x5d6da`、`0x5d82e` 三組 AUIPC/JALR 的呼叫目的均是 `0x2000078a`，**不是 `0x5c9b4`**；`0x5c9b4` 在 a0。候選搬移對應來源 `0x409fa`，把 a0 寫到 `0x20002ef8`，非零時把相鄰旗標設 1，然後返回。來源 `0x42032` 亦有對同一來源 helper 的 JAL（搬移後 PC 不同）。到此仍不能判定首次讀取前這個槽已登記或已被執行。

以 V1.31 carrier 為參數核對目的地址、實參和兩個不同的槽：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes();base=0x40000
def ck(x):
    if not x:raise ValueError('upstream callback evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
def w(p):return int.from_bytes(b[p-base:p-base+4],'little')
def imm(x):return (x>>20^2048)-2048
def jal(p):
    x=w(p);ck(x&4095==239);v=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;return p+(v^0x100000)-0x100000
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck([jal(p) for p in (0x6dd8a,0x5a008,0x5a00c,0x58d18,0x58da2,0x58956,0x5895e,0x5ccee,0x42032)]==[0x5a004,0x60856,0x58ef2,0x58498,0x588b4,0x585c8,0x58498,0x5c830,0x409fa]);raw(0x58f02,'b797050037370020938727c52328f74e8280');ck(0x59000-942==0x58c52 and 0x20003000+1264==0x200034f0)
raw(0x5cce4,'83473a00858b81c72285');raw(0x409fa,'b737002023aca7ee11c5b73700200547238ee7ee8280');ck(0x409fa-0x40270+0x20000000==0x2000078a and 0x20003000-264==0x20002ef8)
for hi,lo,call in [(0x5cf9a,0x5cfa0,0x5cfa8),(0x5d6ca,0x5d6d4,0x5d6da),(0x5d826,0x5d82a,0x5d82e)]:
    ck(w(hi)==0x5d537 and w(lo)==0x9b450513 and (w(hi)&0xfffff000)+imm(w(lo))==0x5c9b4);x=w(call);y=w(call+4);ck(x&4095==151 and y&0xfffff==0x80e7 and (call+(x&0xfffff000)+imm(y))&0xfffffffe==0x2000078a)
print('PASS: 9 JAL edges; 3 callback arguments vs call targets; 2 distinct slots')
```
