# 首次排程要求：ID 來自重讀，不是登記返回暫存器

接續[第一筆 APP 登記](v4160-first-app-registration-order.zh-TW.md)。`0x19b34` 保存登記結果低 byte；`0x19b38` 呼叫 `0x19b56`。正常返回時 `0x19b3a` 先以 **live s0** 為址重讀 unsigned byte 到 a0，才還原 caller 的 s0。`0x19b40` 從 live s1+88 取尾跳目的，後續設定 a1=8192、a2=192000，不再改 a0。若 s0/s1 保持且該 byte 未改，所傳 ID 就是登記值（前輪成功情境為 3，失敗則為 255）。沒有檢查 ID 是否有效；發出要求不等於排程成功。

`0x19b56` 的直線主體有 13 個直接呼叫點，其中四次進 `0x19272`，輪詢 `0x40002804` 的 bit 5，直到置位。若某次一直未置位，便不會走到上述重讀。前六次直接呼叫在所給參數下僅寫外設 `0x4002101c/0x40007000/0x40021024/0x40021020`，沒有直接寫 nominal task byte `0x20004184`。不能把這個結論延伸到所有子呼叫：`0x197b8` 以 3 尾跳 `0x1929a`，後者從 gp+108 載入指標；`0x19bcc` 又以 sp 傳配置給 `[0x40074]`。候選 V1.31 的配置及排程槽分別是 `0x43f46`、`0x43728`，非實機身分證明。尚需分別核對 `0x1929a` 及配置回呼寫入，再判定保存值是否一直有效。

重跑：傳入 decoded APP、V1.31 carrier 路徑。檢查呼叫順序、輪詢與返回後指令，不執行外設。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('task reload mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def read(p,n): return a[p-0x8000:p-0x8000+n]
p=0x19b56; calls=[]
while p<0x19bd4:
    x=int.from_bytes(read(p,4),'little'); n=4 if x&3==3 else 2
    if n==4 and x&0xfff==0xef:
        d=(x>>31<<20)|(x&0xff000)|((x>>20&1)<<11)|((x>>21&1023)<<1)
        calls.append(p+(d^0x100000)-0x100000)
    p+=n
ck(p==0x19bd4 and calls==[0x19142,0x19076,0x190c6,0x1909e,0x190da,0x190e6,0x19272,0x19272,0x19248,0x19272,0x19220,0x19272,0x197b8])
ck(read(0x19272,16).hex()=='373700408357478093f70702e5df8280')
ck(read(0x19b38,30).hex()=='392803450400224403a38405b240924437f60200130606e0896541010283')
ck(read(0x197b8,6).hex()=='0d456ff01fae' and read(0x19bc8,12).hex()=='fc5b0a858297f24005618280')
ck([int.from_bytes(b[i:i+4],'little') for i in (0x74,0x58)]==[0x43f46,0x43728])
print('PASS: 13 direct calls; 4 poll sites; unsigned task reload before tail')
```
