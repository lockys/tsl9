# 槽 3、4：直接轉移後，取消碼是否仍在 a0？

限 V1.31 參考映射與 WCH 壓縮指令解讀，承接[入口分析](v4160-state67-callback-bindings.zh-TW.md)。兩處尾跳 `0x605e0 → 0x6020a`、`0x58d3c → 0x57dae` 都不設返回位址；依[既有 callee 分析](v4160-idle-callees-first-a0.zh-TW.md)，可以原值返回，或先寫常數 6／3。寫入常數 6 即使與取消碼相等，也不是沿用輸入。

四處 AUIPC/JALR（`0x60592`、`0x60674`、`0x606e8`、`0x58d88`，各為指令對起點）都呼叫同一個 RAM 輪詢函式 `0x20002610`。它可以等待不返回；正常返回並不讀寫 a0，因此還要看各呼叫點的續段。

另一路 `0x60708 → 0x5f0d2` 可以再縮小：入口到 `0x5f19a` 沒碰 a0；這裡也呼叫 `0x20002610`，接著 `0x5f19e` 呼叫 `0x63e58`。後者在本次分支遍歷只有 `0x63ed8` 返回，未碰 a0。兩者正常返回後，依 `[s7+1300]` 的 bit 0，首次碰觸是 `0x5f1aa: mv a0,s0`（1），或 `0x5f1bc: lbu a0,40(s0)`（0）。故這一路沒有先消費取消碼；即使新值恰為 6 也已換了來源。不保證輪詢結束、參考碼已安裝或實機必走此路。

重現：在 repo 根目錄將 V1.31 carrier 作為參數，以 Python 執行下段。沿用入口分析的受限遍歷器，非獨立 CPU 實作。

```python
from pathlib import Path
from hashlib import sha256
from runpy import run_path
import sys
b=Path(sys.argv[1]).read_bytes(); m=run_path('analysis/check_v131_slots34.py'); ck,sx,walk=(m[k] for k in ('ck','sx','walk'))
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p):return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
for p in (0x60592,0x60674,0x606e8,0x58d88,0x5f196):
    x,y=w(p),w(p+4);ck(x&4095==0x97 and y&0xfffff==0x80e7);ck((p+(x&0xfffff000)+sx(y>>20,12))&0xfffffffe==0x20002610)
for p,rd,t in ((0x605e0,0,0x6020a),(0x58d3c,0,0x57dae),(0x60708,1,0x5f0d2),(0x5f19e,1,0x63e58)):
    x=w(p);d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==rd<<7|111 and p+sx(d,21)==t)
for p,e,ends in ((0x5f0d2,0x5f19e,[(0x5f19a,'transfer')]),(0x63e58,0x63eda,[(0x63ed8,'ret')]),(0x5f1a2,0x5f1c0,[(0x5f1aa,'overwrite'),(0x5f1bc,'overwrite')])):
    ck(walk(b,p,e)==ends)
ck(w(0x5f1aa)&65535==0x8522 and w(0x5f1bc)==0x02844503)
print('PASS: 5 poll calls, 4 JAL targets, 3 bounded walks, 2 first overwrites')
```
