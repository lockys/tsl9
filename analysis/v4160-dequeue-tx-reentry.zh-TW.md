# 出列記錄進入 0x8a56：在哪裡才依賴 resident？

接續 [0x82d2 出列路徑](v4160-dequeue-first-call.zh-TW.md)。`0x8358` 重新以 LBU 讀長度，`0x8362` 加 2，故 `0x8368` 傳給 TX 的長度一定在 **2..257**；即使先前的 0..8 樣本過期，此呼叫仍不會走 `0x8a5a` 的長度過大返回。handle 也是在複製後從 T+2 重讀的半字，不能假設仍符合先前的檢查。

- 對入口 handle H，先比較 `U16[gp+150]`，再視分支比較 `U16[gp+154]`。若 H 是 `0xfffe` 或兩次比對均不符，直接由 `0x8aca` 返回；沒有 TX 子呼叫、沒有經事件槽尾跳，也就不會在這段經服務重入初始化。呼叫者先前的複製不在這個排除範圍。
- 首筆相符且非 sentinel 時，`0x8a8e` 經 `[0x4013c]` 查詢。只有返回 **恰等於 1** 才選 bank 0；否則再取第二個 handle。第二筆相符且非 sentinel 時，`0x8ab4` 重新讀槽後呼叫；恰等於 1 選 bank 1，否則返回。若兩筆同值，第一次未通過不等於本輪必然退出。此描述假定返回後 s2 等必要狀態正常保存。
- 選 bank 後，APP 封包及 checksum 迴圈沒有 call；正常完成才以 `a0=U8[gp+148+4*bank]`、`a1=1` 從 `0x8b50` 尾跳 `[0x40050]`（目標清低位）。V1.31 參考的[事件服務](v4160-first-timer-due-post.zh-TW.md)是設 pending bit，不是同步呼叫 handler。這不證明目前設備的兩個服務槽或後續事件派送；也不把未選 bank 但已進查詢服務的路徑列為無呼叫。

重現：傳入原始 v4.1.60 BIN。從實際 B-type 編碼解分支的比較與目標；查詢回傳與第二次 handle 樣本是合成輸入，測到 bank 選定或原位返回即停，不執行 provider。

```python
from pathlib import Path
from hashlib import sha256
from itertools import product
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('TX dispatch mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(pc,n): return b[pc-32768:pc-32768+n]
def branch(pc,r):
    w=int.from_bytes(raw(pc,4),'little'); ck(w&127==99)
    a=r[w>>15&31]; c=r[w>>20&31]; f=w>>12&7
    d=((w>>31)<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    return pc+((d^4096)-4096) if {0:a==c,1:a!=c,6:a<c}[f] else pc+4
ck(raw(0x8358,4).hex()=='83c62400' and raw(0x8362,2).hex()=='8906')
for n in range(256): ck(branch(0x8a5a,{15:1039,13:n+2})==0x8a5e)
for h,x,y,u,v in product((1,2,65534),repeat=5):
    # u,v are independent statuses: 1 succeeds; 2 and 65534 do not.
    calls=[]; bank=None
    if branch(0x8a76,{14:x,10:h})==0x8a7a and branch(0x8a7e,{14:x,15:65534})==0x8a82:
        calls.append(0); bank=0 if branch(0x8a92,{10:u,15:1})==0x8acc else None
    if bank is None and branch(0x8a9a,{15:y,18:h})==0x8a9e and branch(0x8aa2,{18:h,15:65534})==0x8aa6:
        calls.append(1); bank=1 if branch(0x8aba,{10:v,15:1})==0x8ace else None
    eligible=[i for i,k in enumerate((x,y)) if k==h!=65534]; expected=[]; chosen=None
    for i in eligible:
        expected.append(i)
        if (u,v)[i]==1: chosen=i; break
    ck((calls,bank)==(expected,chosen))
ck(raw(0x8a8e,2)==raw(0x8ab4,2)==bytes.fromhex('8297') and raw(0x8b50,2).hex()=='0283')
print('PASS: 256 caller lengths; 243 handle/status combinations; 2 query sites and 1 tail transfer')
```
