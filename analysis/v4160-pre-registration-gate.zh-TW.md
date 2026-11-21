# 在六次直接登記之前，還有一次有條件的登記

修正[角色登記序列](v4160-role-registration-ledger.zh-TW.md)的名義起算點。`0x6dd1a → 0x61b1c → 0x55bde` 讀的是 `0x2000319f`，不是計數 `0x2000319d`，也不是共用 ID `0x200035f5`。若該 byte 非零，`0x55bea` 跳過登記。若為零，`0x55bf4` 先以 handler `0x5352c` 呼叫 `0x43c4e`，再將結果交給 `0x5362e`；後者在 `0x53668` 把保存值的低 byte 寫回 `0x2000319f`（要求正常返回及保存 s0）。因此這不是無條件不影響計數的前置函式。

| 讀到的值 | 前置登記 | 六次直接登記用去的 ID | 隨後共用 ID / 第二角色 ID |
|---|---|---|---|
| 0 | ID 5 | 6..11 | 12 / 13 |
| 1..255 | 跳過 | 5..10 | 11 / 12 |

表格假設進入時計數 5、容量 29，後續登記正常、初始共用 ID 為 255，沒有其他計數或 ID 改寫。兩條路徑都使共用 ID 不再是 255，因此**這一處分支會改變 ID 數值，不會單獨翻轉先前的旗標判斷**。前置函式會合後的七筆固定 word 寫入已另行[盤點](v4160-role-before-count.zh-TW.md)。`0x43b80` 名義上清除的 40 bytes 包含 `0x2000319f`，所以不能把非零路徑當成預設；尚未證明清零後直到這次讀取都沒有其他寫入。V1.31 是參考 ROM，未確認裝置版本或執行狀態。

重現：下列局部檢查以參考 carrier 路徑為參數，核對分支與呼叫、讀寫的 byte 和名義登記計算，不是全初始化模擬。

```python
import sys
from pathlib import Path
from hashlib import sha256
b=Path(sys.argv[1]).read_bytes()
def need(ok):
    if not ok: raise ValueError('pre-registration evidence mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def u(p,n=4): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    x=u(p); need(x&4095==0xef)
    return p+sx(x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
need([jal(p) for p in (0x6dd1a,0x61b20,0x55bf4,0x55bf8)]==[0x61b1c,0x55bde,0x43c4e,0x5362e])
need(u(0x55bde)==0x200037b7 and u(0x55be2)==0x19f7c783 and u(0x55bea,2)==0xeb89)
h=u(0x55bea,2); disp=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
need(0x55bea+sx(disp,9)==0x55bfc and (u(0x55bec)&~4095)+sx(u(0x55bf0)>>20,12)==0x5352c)
need(u(0x53642,2)==0x842a and u(0x53664)==0x200037b7 and u(0x53668)==0x18878fa3)
for gate in range(256):
    count=5; ids=[]
    for _ in range(8+int(gate==0)):
        need(count<29); ids.append(count); count+=1
    need(ids[-2:]==([12,13] if gate==0 else [11,12]))
print('PASS: four call edges, zero/nonzero branch, gate writeback; 256 nominal ID sequences')
```
