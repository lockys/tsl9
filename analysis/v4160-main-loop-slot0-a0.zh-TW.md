# 主迴圈 0x819c：取消值能傳入另一層回呼，但不是這裡的分支條件

原 APP 的 `0x818c` 把 s2 設為 `0x20000000`；每輪 `0x8198` 從當時的 `[s2]` 載入 a5，再 `jalr a5`。這不是固定呼叫 ROM 位址；續輪需要 s2 保持／恢復原值。

**指標來源。** V1.31 參考啟動在 `0x6de1c` 把 `0x200007d0` 寫到 `[0x20000000]`。首段搬移起點是 `0x402b0 → 0x20000040`，不覆寫首槽；因而候選入口的原始位元組在 `0x40a40`。不可直接把 `0x40270` 的第一個 word 當成該槽內容。

**一條保留 a0 的路徑。** 入口保存七個暫存器，沒有保存或讀取 a0。在 Xwchc 解讀下，`0x200007e8` 為 `lbu a5,12(a5)`，採樣 `0x20003240`。若該 byte 非零，`0x200007f6` 跳至 `0x2000081a`。此時 s0 是 `0x200031c8`，`lw a5,8(s0)` 從 `0x200031d0` 取回呼指標。非零才在 `0x2000081e` 間接呼叫；至此沒有指令讀寫 a0。若上游 a0 是 6，它就原樣到達該回呼，但不代表回呼使用它。若指標為零則跳到 `0x20000820`，不是呼叫空指標。

條件：參考啟動與搬移完成、槽未被改寫、記憶體讀寫成功。這不是 ROM 安裝證明。採樣 byte 為零另走 `0x200007f8`，不以這一條路徑概括整個函式。以下接受 decoded APP 與 V1.31 carrier 兩個檔案，固定身分並核對選路所需的指令。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(f).read_bytes() for f in sys.argv[1:])
def ck(ok):
    if not ok: raise ValueError('slot0 path mismatch')
def raw(buf,off,h):
    v=bytes.fromhex(h);ck(buf[off:off+len(v)]==v)
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(a,0x18c,'37090020b73400401304a4aa832709008297')
raw(b,0x2de0e,'3707002006c6b70700201307077d98c3')
raw(b,0x2de30,'37360020b70500203705040098c7130606e7938505041305052b')
p=0x2b0+0x7d0-0x40;ck(p==0xa40)
raw(b,p,'011126cab734002022cc4ac89387442306ce4ec652c456c2dc2737390020938444231304891c95e3')
x=int.from_bytes(b[p+24:p+26],'little');ck(x&0xe003==0x2000 and ((x>>2)&7,(x>>7)&7)==(7,7))
d=(x>>12&1)|(x>>5&3)<<1|(x>>10&3)<<3;ck(0x20003234+d==0x20003240)
raw(b,p+0x4a,'1c4491c38297');ck(0x200031c8+8==0x200031d0)
print('PASS: APP slot load, V1.31 installed value and relocated entry, Xwchc byte gate, nested callback boundary')
```
