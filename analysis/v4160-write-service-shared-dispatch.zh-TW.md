# 兩個上層呼叫點共用事件處理函式與框架（V1.31 參考映像）

[上回](v4160-write-service-upper-edges.zh-TW.md)的 `0x4d484`、`0x4d4b2` 是同一候選入口 `0x4d1b0` 的兩個分支。依據不是位址相近，而是能從共用的選擇值載入指令沿條件跳轉走到兩處，且兩處返回後都跳至 `0x4d2cc`。

* `0x4d1b0..0x4d1b6` 測 a1 的低半字符號位；未設位則走 `0x4d4b8` 回零，不配置框架。另一側 `0x4d1c2` 扣 48 bytes。正常子呼叫返回並保持 SP、不切換堆疊時，若通過後續門檻，可由 `0x4d1fe` 或 `0x4d214` 進入 `0x4d244`。共同出口 `0x4d240` 加回 48、`0x4d242` 返回。下方兩個呼叫點不是兩個連續堆疊層。
* `0x4d258` 重新取 `s2 = U8[s0+4]`。此後選擇值 18 或 24 都跳過 2、6、8、10、12、14、16 七個比較。18 在 `0x4d476` 落下，到 `0x4d484` 呼叫 `0x4bdc6`；24 繼續跳過 18、22，在 `0x4d4a8` 落下，到 `0x4d4b2` 呼叫 `0x4bbc6`。因此在這一輪比較中兩條路徑互斥，不是先後呼叫。
* 這不涵蓋第三處 `0x6c26e`，也不證任何事件在裝置上出現。上層絕對 SP 和實際安裝的 ROM 仍未知。

重現：傳入固定 V1.31 主區段 BIN。以下從實際指令解出每個比較常數、暫存器與跳轉目標，對 256 個選擇值分類；不模擬子呼叫或其他 case 的內部流程。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('dispatch evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p,n): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
ck(w(0x4d1c2,2)==0x7179 and w(0x4d240,4)==0x80826145 and w(0x4d258,4)==0x00444903)
pcs=[0x4d25c,0x4d2bc,0x4d2f0,0x4d302,0x4d378,0x4d450,0x4d462,0x4d474,0x4d48a,0x4d4a6]
rows={}
for i,p in enumerate(pcs):
    h=w(p,2); ck(h&0xff83==0x4781); v=h>>2&31
    q=0x4d268 if i==0 else p+2; x=w(q,4); ck(x&0x01fff07f==0x00f91063)
    d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    nxt=q+((d^4096)-4096); ck(nxt==(pcs[i+1] if i+1<len(pcs) else 0x4d290)); rows[p]=(v,q+4,nxt)
ck(w(0x4d484,4)==0x943fe0ef and w(0x4d4b2,4)==0xf14fe0ef)
for v in range(256):
    p=pcs[0]
    while p in rows:
        k,eq,ne=rows[p]; p=eq if v==k else ne
    ck((p==0x4d47a)==(v==18) and (p==0x4d4ac)==(v==24))
print('PASS: 10 comparisons, 256 selectors, distinct arms in one 48-byte frame')
```
