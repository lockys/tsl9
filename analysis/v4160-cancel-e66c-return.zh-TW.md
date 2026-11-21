# 0xe66c 取消返回後：入口守衛排除了另一條尾跳

只追 v4.1.60 APP 的 `0xe546` 這條路。`[gp+84]` 指向的首 byte 要有 `0x10`，且無號 s0 不等於 63、不小於 63、不大於 66，才走到 `0xe66a: li a0,0` 和 `0xe66c: jal ra,0xd668`。所以呼叫前 s0 只能是 **64、65、66**。

取消若正常返回並保存 s0，`0xe670` 跳到 `0xe568`，三個值均大於 61，走 `0xe672`。`(s0-68)&255` 分別是 252、253、254，都大於 1，故到 `0xe736` 還原暫存器和 sp，`0xe740: ret`。這段**不讀也不改 a0**；若取消結果為 6，它原樣返回上層。這不是上層一定使用 6 的證明。

不能把共用出口的所有分支算在這次取消上：若單獨從 `0xe568` 注入 byte 值 1..16、60、61、68、69，則走 `0xe58e` 尾跳 `0x171de`，再呼叫 `0x8440`，由 `lbu a0,364(gp)` 覆寫。這 20 個值與本呼叫前的三值無交集。若 s0 跨呼叫被改寫，需依實際返回狀態另判；沒有假設安裝哪一版 ROM。

重現：傳入原 decoded BIN。檢查原指令視窗，解出分支位移，再分別測入口與出口（不是整機模擬）。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('e66c trace mismatch')
def at(p,n): return b[p-0x8000:p-0x8000+n]
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for p,h in [(0xe546,'938741059c4383c70700c18b99cb9307f0036301f4106366f4009307200463f38710'),(0xe66a,'0145efe0dfffe5bd1304c4fb1374f40f854711b7'),(0xe568,'9307d00363e387109307c0036378f4007d141374f40fbd4763eb871a2244b2409244024941016f801045'),(0xe736,'b24022449244024941018280'),(0x171de,'411106c622c426c2ef10afa5'),(0x8440,'03c5c1168280')]:
    v=bytes.fromhex(h);ck(at(p,len(v))==v)
def dest(p):
    x=int.from_bytes(at(p,4),'little');d=(x>>31)<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    return p+(d^4096)-4096
def end(s):
    if s>61:
        ck(dest(0xe56c)==0xe672);n=(s-68)&255;limit=1
    elif s>=60:return dest(0xe574)
    else:n=(s-1)&255;limit=15
    return dest(0xe580) if n>limit else 0xe584
ck([dest(p) for p in (0xe558,0xe55c,0xe564)]==[0xe65a,0xe568,0xe66a])
entries={(f,s) for f in range(256) for s in range(256) if f&16 and s!=63 and s>=63 and s<=66}
ck(len(entries)==384 and {s for f,s in entries}=={64,65,66} and all(end(s)==0xe736 for f,s in entries))
ck([s for s in range(256) if end(s)==0xe584]==[*range(1,17),60,61,68,69]);print('PASS: 65536 flag/selector pairs; 384 enter; all preserve a0 to ret under s0 preservation')
```
