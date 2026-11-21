# `0x20003220`：配置失敗回呼的初值

沿著[配置器失敗分支](v4160-role-allocator-metadata.zh-TW.md)往前找，`0x20003220` 是複製後設定結構的 **+52**，不是 APP 的 `sp+52`。結論：在 v4.1.60 APP 配上 V1.31 參考 ROM、清零及複製正常完成時，此次設定**未提供失敗回呼**。這是設定來源的結論，不是 `0x4ee08` 呼叫時的 RAM 快照。

1. 參考啟動清零的 456 個 word 從 `0x20002ef8` 起；第 203 個是 `0x20003220`。但後來的設定複製會重寫這整個 word，不能只依啟動清零推論。
2. APP 在 `0x19a38` 要求把 `[sp+16,sp+80)` 清零。欲查的四個 byte 是 `sp+68..71`。清零後的 14 筆直接 stack store、helper 的 `sp+8..13` 和複製迴圈的 `sp+40..45` 均未覆蓋。相鄰的 `sp+64` 和 `sp+72` 均有寫入，不能把它們誤認成失敗回呼。
3. APP `0x19aec` 傳入 `sp+16`；參考 `0x43cda..0x43ce8` 要求複製 64 bytes 至 `0x200031ec`。故 `[0x20003220]` 此時為零。接下來 `0x43cf8..0x43d32` 的八個條件式預設欄位寫入亦不觸及 `+52..55`。
4. `0x43d34..0x43d38` 檢查並呼叫的是 **+44**，其 APP 來源為 `sp+60`，PC-relative 值 `0x197f0`。這是另一個可能在複製後執行的函式，不是配置失敗回呼；單憑設定值不能排除後續寫入。配置器抵達 sentinel 且重新讀到零才會略過失敗回呼。

重現：先對原 APP 跑 `analysis/check_v4160_cfg12_writes.py` 確認完整直接寫入清單，對參考 carrier 跑 `analysis/check_v131_startup_clear_3350.py` 核對清零範圍；再將下列程式以 APP、carrier 為參數執行。此核對不含中斷、外設副作用或實際 ROM 身分。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(s).read_bytes() for s in sys.argv[1:])
def need(p):
    if not p: raise ValueError('evidence mismatch')
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
slot=0x20003220; field=slot-0x200031ec
need(field==52 and (slot-0x20002ef8)//4+1==203)
ranges=[(16,4),(20,2),(24,4),(30,2),(32,2),(34,1),(36,2),(72,4),(76,4),(52,4),(46,2),(60,4),(48,2),(64,4),(8,6),(40,6)]
need(all(not set(range(16+field,20+field)).intersection(range(o,o+n)) for o,n in ranges))
for p in (0x43cf8,0x43d00,0x43d08,0x43d10,0x43d18,0x43d20,0x43d28,0x43d32):
    h=int.from_bytes(b[p-0x40000:p-0x40000+2],'little'); q=h&3
    need(h>>13==5 and q in (0,2) and 8+(h>>7&7)==15)
    off=(8*(h>>10&7)+2*(h>>5&3)) if q==2 else (8*(h>>10&3)+2*(h>>5&3)+(h>>12&1))
    need(off+(2 if q==2 else 1)<=field)
need(a[0x11a92:0x11a9a].hex()=='970700009387e7d5' and a[0x11a9e:0x11aa0].hex()=='3ede')
need(0x19a92+(int.from_bytes(a[0x11a96:0x11a9a],'little',signed=True)>>20)==0x197f0)
print('PASS: clear word #203; cfg+52 = sp+68 untouched; 8 defaults disjoint; separate cfg+44 target')
```
