# 啟動時的參數設定：先解間接跳表，再追仍有子呼叫的分支

問題是 `0x8fcc` 註冊 APP 四列之前，resident 有沒有先分配 GATT handle。以原 APP 的參數選路，不把 setter 的整張跳表都視為可達。下列結果以 V1.31 參考表、Xwchc、參數與堆疊正常為條件。

| APP 呼叫點 | 參數 | 參考 resident 的實際分支 |
|---|---|---|
| `0x8ef6` | 774，長 13 | `0x6d910` 檢查長度及指標，正常尾跳 `0x48790`；先以 21 bytes 要求配置。這條路徑不能標為無子呼叫。 |
| `0x8f04 / 0x8f14` | 785 / 786，長 2，值 6 / 1000 | `0x6d9c8 / 0x6d9ee` 檢查長度及無號半字值 6..3200；通過則寫 `0x200035c8 / 0x200035d2` 後返回，兩個分支都不呼叫服務註冊。 |
| `0x8f20 / 0x8f2c / 0x8f5c` | 3 / 4 / 可選 25 | `0x46506` 內三個子呼叫分別只對 selector 17、58、59。這三個 APP selector 都不選它們；值非 `0xffff` 則走共同寫入路徑。 |
| `0x8f30 → 0x8b88` | 773，長 1，值 1 | `0x6d8aa` 更新 enable byte；舊值非零則返回。舊值為零，狀態 word 等於 1 或低四位為 3、4 時呼叫 `0x4354a(task,1)`，是設 pending bit，不是同步執行 handler。 |
| `0x8f74` | 1024，長 1，值 0 | `0x6c40c` 接受 0..2，寫 `0x20002ef6` 後返回；不是寫 handle 游標 `0x20002eec`。 |

因此兩個 interval 設定、三個 scalar 設定及 selector 1024 本身不是提前註冊來源。接下來優先追 **774 的 `0x48790`** 成功配置後的分支；不假設 allocator 或稍後事件沒有副作用，也不據此指派四列的實機 handle。

複核方式：從 repo 根目錄執行以下 Python，參數為原 APP、V1.31 主區。驗證限定為表項、實際常數及指定轉移，不是整段執行。

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
a,r=[Path(p).read_bytes() for p in sys.argv[1:]]
def need(v):
    if not v: raise ValueError('parameter dispatch mismatch')
need([sha256(x).hexdigest() for x in (a,r)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def word(b,i): return int.from_bytes(b[i:i+4],'little')
need([word(r,i) for i in (372,340,360)]==[0x6d834,0x46506,0x6c3d6])
for pc,sel,target in [(0x8b84,773,0x6d8aa),(0x8ef2,774,0x6d910),(0x8f00,785,0x6d9c8),(0x8f10,786,0x6d9ee),(0x8f70,1024,0x6c40c)]:
    need(word(a,pc-0x8000)==(sel<<20|0x513))
    off=0x2e74c if sel==1024 else 0x2e900+4*(sel-769)
    need(word(r,off)==target)
for pc,t in [(0x6d920,0x48790),(0x487ca,0x20000040),(0x6d90a,0x4354a),(0x4652c,0x533c2),(0x46554,0x53356),(0x46566,0x5335a)]:
    need(any(int(site,16)==pc for site,_,_ in edges(r[pc-0x40000:pc-0x40000+8],pc,t)))
need([v for v in range(65536) if ((v-6)&65535)<=4096-902]==list(range(6,3201)))
print('PASS: 3 slots, 5 parameter jump-table entries, 6 transfers, 65536 interval values')
```
