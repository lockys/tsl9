# 首次設定 774 之前，廣播處理函式的 enable byte 可以已是 1

不要用「尚未設定廣播資料」推論 `U8[0x200035a8] == 0`。原 APP 在 `0x8eb6` 先經角色槽呼叫，之後才在 `0x8ef6` 設定 774。若槽為 V1.31 參考的 `0x6dd16`，該角色初始化路徑的 `0x6dd3a` 呼叫 `0x46570`；它先連續呼叫 `0x45220`、`0x48c56`、`0x47eac`。若都正常返回，`0x46582` 呼叫 `0x6d682`。其 `0x6d694` 設 a3=1，`0x6d69a` 設 a5=`0x20003000`，`0x6d69e` 執行 `sb a3,1448(a5)`。這個寫入**不需要先派送事件**。相反，已知主迴圈派送點 `0x819c` 要等外層初始化正常返回才會進入，不能用它解釋首次設定之前的派送。

這裡寫的是單一 enable byte，不是 12-byte 物件指標 `0x20002f14`，也不是 pending mask。即使 enable 為 1，仍須另證 bit 0 被投遞並由對應 handler 處理。未排除初始化內嵌的其他間接呼叫、中斷或後續寫入；不推論實機採用這版 ROM。

複核：原 APP 的 `check_v4160_role_init_args.py` 與[主迴圈呼叫順序](v4160-main-loop-config-reentry.zh-TW.md)；以下在 repo 根目錄以 V1.31 主區為唯一參數執行。

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
r=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('enable initialization mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for pc,t in [(0x6dd3a,0x46570),(0x46576,0x45220),(0x4657a,0x48c56),(0x4657e,0x47eac),(0x46582,0x6d682)]:
    ck(edges(r[pc-0x40000:pc-0x40000+4],pc,t)==[(hex(pc),'JAL',1)])
ck(r[0x2d690:0x2d6a2].hex()=='b73700208546238a075eb73700202384d75a')
w=int.from_bytes(r[0x2d69e:0x2d6a2],'little'); off=(w>>25)<<5|(w>>7&31)
ck((w&127,w>>12&7,w>>15&31,w>>20&31,0x20003000+off)==(35,0,15,13,0x200035a8))
print('PASS: 5 direct calls; enable byte store to 0x200035a8')
```
