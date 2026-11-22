# 三個角色入口：第一個可再次把 handle 游標設為 1

原 APP 的三個間接呼叫若使用 V1.31 參考表，依序落在 `0x6dd16`、`0x6dd86`、`0x66056`。第一個入口的 `0x6dd7a` 呼叫 `0x4d172`；其中 `0x4d17e` 呼叫 `0x4b35e`。只要前面的服務都正常返回並走到 `0x4b38c`，這裡會執行 `sh a1,-276(a5)`，此時 `a5=0x20003000, a1=1`。因此 **`0x20002eec` 再次被設為 1**；僅累加自啟動以來的註冊次數會算錯。第二個入口也有 `0x6de00 -> 0x4d172`，但若 `0x6dda0` 跳至 `0x6de04` 就跳過。前置 byte 取自 `0x200035f5`；值 1..254 跳過，0 或 255 不跳過。第三個入口則沒有這一條直接呼叫。

**準備四列不等於分配四個 handle。** 同一初始化函式在 `0x4b3c6` 清除 `0x20002f7c` 的旗標，並準備四列和回呼表，最後在 `0x4b454` 返回。另一入口 `0x4cf96` 才讀這個旗標：在 Xwchc 解讀下，若已非零就跳過；若為零則先寫 1，再測輸入 `a0 & 1`，為零也跳過。只有兩關均放行才在 `0x4cfbe` 帶入表 `0x20002e7c`、列數 4、參數 16、回呼表 `0x20002ebc` 尾跳。旗標為 1 本身不能證明曾分配成功。尚未證明在最後一次重設與 APP 註冊之間實際進入這個入口，也未排除動態列數入口。

複核（以 V1.31 主 carrier 為唯一參數；只讀，不執行韌體）：

```python
import hashlib, sys
from pathlib import Path
r = Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('role/cursor evidence mismatch')
need(hashlib.sha256(r).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(pc): return int.from_bytes(r[pc-0x40000:pc-0x40000+4], 'little')
need([word(p) for p in (0x401a0,0x401ac,0x401c0,0x40134)] == [0x6dd16,0x6dd86,0x66056,0x4cf96])
for pc,target,rd in [(0x6dd7a,0x4d172,1),(0x6de00,0x4d172,1),(0x4d17e,0x4b35e,1),(0x4cfbe,0x4cf22,0)]:
    w=word(pc); j=(w>>31<<20)|(w&0xff000)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    need(w&4095 == rd*128+111 and pc+j-((j>>20)<<21)==target)
for pc,h in [(0x4b386,'8545b73700202396b7ee'),(0x4b3c2,'b7370020238e07f6'),(0x6dd92,'83c7575f1307d00ffd1793f7f70f6372f706'),(0x4cf96,'b73700209387c7f798230de3054798a3058909cd'),(0x4cfaa,'b7360020373500209386c6eb414691451305c5e7')]:
    need(r[pc-0x40000:pc-0x40000+len(h)//2].hex()==h)
need([b for b in range(256) if ((b-1)&255)>253] == [0,255])
print('PASS: 4 slots, 4 transfers, cursor reset, separate registration gate')
```
