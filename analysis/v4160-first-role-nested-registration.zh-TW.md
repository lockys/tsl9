# `0x42032` 不是啟動時無條件登記

接續[延後執行回呼](v4160-role-before-deferred-runner.zh-TW.md)。在 V1.31 參考映像中，先區分兩層登記，再判斷初始化時序。

* `0x5cd2c` 與 `0x5d7bc` 呼叫 `0x43ed2`，不是呼叫 `0x20001caa`。後者是 a0 的值，對應來源 `0x41f1a` 搬移後的入口。`0x43ed2` 只將 a0 寫到 `0x20003244` 就返回。特別是 `0x5cd2c` 已位於 `0x5c9b4` 的函式內，不能用該次登記反證 `0x5c9b4` 已被首次啟動。
* 即使另有程式呼叫 `0x20001caa`，該函式先讀 `U32[0x20003410]`，零即返回 1；非零才讀 `U32[第一個指標+172]`，第二個指標為零也返回 1。這兩條退出都在內層登記之前。`0x20003410` 在候選正常啟動清零範圍內，但這不足以證明之後一直為零。
* 在通往 `0x42032` 的局部分支，`0x41fc8` 要求 a5=168，`0x42026` 要求 s2=a2，才會沿所列直落路徑把 `0x5c9b4` 交給 setter（`0x409fa` 搬移後的位址）。後者寫到另一槽 `0x20002ef8`。以上都不是執行回呼的證據。首次 `0x55bde` 前，尚未確定 `0x20003244` 是否已登記並被讀者呼叫，以及兩層指標是否已建立；其他登記來源仍分開處理。

重現：以 V1.31 carrier 為參數。驗證兩次外層 JAL、兩條壓縮零指標分支、兩條內層比較與搬移後 JAL。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes();base=0x40000
def ck(x):
    if not x:raise ValueError('nested registration evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
def w(p):return int.from_bytes(b[p-base:p-base+4],'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    x=w(p);ck(x&4095==239);return p+sx(x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
def bz(p,r):
    h=w(p)&65535;ck(h&0xe003==0xc001 and 8+(h>>7&7)==r);return p+sx((h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5,9)
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for hi,lo,p in [(0x5cd22,0x5cd28,0x5cd2c),(0x5d7b2,0x5d7b8,0x5d7bc)]:
    ck(w(hi)==0x20002537 and w(lo)==0xcaa50513 and (w(hi)&0xfffff000)+sx(w(lo)>>20,12)==0x41f1a-0x40270+0x20000000 and jal(p)==0x43ed2)
raw(0x43ed2,'b737002023a2a7248280');raw(0x41f22,'83a40741');raw(0x41f2c,'8547c1c403a4c40a854741c0');ck(bz(0x41f2e,9)==bz(0x41f36,8)==0x41fb6);raw(0x41fbe,'3e8541018280')
raw(0x41fc4,'1307800ae399e7fc');raw(0x42026,'e31ac9f637d505001305459b');ck(jal(0x42032)-0x40270+0x20000000==0x2000078a);raw(0x409fa,'b737002023aca7ee');print('PASS: two outer registrations; two null exits; conditional inner registration')
```
