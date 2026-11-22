# `0x6b928` 配置的是 `0x6b286` 重新載入的列陣列

V1.31 參考映像，依 Xwchc 解讀。`0x6b948` 讀 cfg+14 的 byte（n₀）；`0x6b95c/960` 清除列數 `0x20002fc1` 與指標 `0x20002fbc`；接著呼叫 `0x20000040(16*n₀,66)`。`0x6b96c` 把返回值 P 寫進該指標欄位，零值直接跳過初始化迴圈。非零時，`0x6b978` **再讀一次** cfg+14，把 n₁ 寫入列數；`0x6b984` 每輪重讀列數。不能只用第一次的配置大小推論後來所有索引有效。

對索引 i，初始化迴圈三次取 P，先要求填 `ff` 到列偏移 0..5、6..11，再清偏移 12..13 的半字及偏移 14 的 byte；沒有直接清偏移 15。後來的 [`0x6b286`](v4160-replay-410-subcalls.zh-TW.md) 用同一指標欄位，讀取要求涵蓋完整 16 bytes，讀失敗才走填值路徑。

若配置成功、P 維持在名義 arena（payload 起點至少 `0x200043b4`）、沒有位址回繞且每次 i<n₀，這些列寫入不會指到較低的旗標 `0x20002ef0`。這只排除**透過列資料的寫入**；初始化函式後段另有[直接寫旗標的 `0x6ba8c`](v4160-replay-flush-flag-origin.zh-TW.md)。不代表所有回呼保持 P、兩次計數相同或實機使用這份 ROM。

重現：傳入 V1.31 參考 BIN；核對兩次取樣、配置交接、列初始化尾段，以及所有 byte 配置數的列範圍。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('row allocation evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,h):
    z=bytes.fromhex(h); ck(b[p-0x40000:p-0x40000+len(z)]==z)
raw(0x6b944,'9387c91e e827 37390020 37340020 9304c9fb 93052004 1205 a30004fc 23a00400 9740f91f e780c06d 88c0 130414fc 05c5')
h=int.from_bytes(b[0x2b948:0x2b94a],'little'); ck((h&3,h>>13,(h>>7&7)+8,(h>>2&7)+8,(h>>12&1)|(h>>10&3)<<3|(h>>5&3)<<1)==(0,1,15,10,14))
ck(0x6b964+0x1ff94000+1756==0x20000040 and 0x20003000-68==0x20002fbc)
raw(0x6b974,'9389c91e 83c7e900 1309c9fb 8144 1ca0 1c20 63e5f412')
raw(0x6bab0,'03250900 139a4400 1946 9305f00f 5295 9750f91f e780c08d 03250900 1946 9305f00f 5295 1905 9750f91f e780608c 83270900 8504 93f4f40f d297 23960700 23870700 49bd')
k=0
for n in range(256):
    for i in range(n):
        ck(16*i+15<16*n and 0x20002ef0<0x200043b4+16*i); k+=1
ck(k==32640)
print('PASS: allocation slot; two count samples; 32640 in-bounds rows')
```
