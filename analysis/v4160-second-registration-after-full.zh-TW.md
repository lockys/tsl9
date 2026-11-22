# 第一次滿表後，第二次登記會不會成功？

第二次登記並不沿用第一次的 ID。`90a2` 以 `901a` 作參數，V1.31 候選服務重新讀相鄰兩個 byte：計數 `0x2000319d`、容量 `0x2000319e`。要從第一次結果推到第二次，須排除這兩個 byte 在中間改變，而不是只證明 APP 繼續執行。

針對第一次滿表、APP 仍讀回 255 的路徑，從 `43728` 排程入口到第二次登記前：

* `43754` 在讀完計數後跳到 `43764`，跳過時鐘與配置。排程器九筆 stack store 在名義入口 SP−36 至 SP（不含），另寫 `0x4002420c` 清除／還原控制 word；沒有改這兩個 byte。
* 排程正常返回後，`8eb0 → 907a` 的兩個保存 word 在入口 SP−8 至 SP（不含）。唯一中間呼叫 `9094` 的[參考填值函式](v4160-final-init-saved-base.zh-TW.md)清除 `[0x2000be08,0x2000bebc)` 並操作同一外設 word；這些直接寫入也不碰計數或容量。

所以，若第一次滿表狀態保持到排程入口（包括[校時呼叫](v4160-task-clock-copy16.zh-TW.md)這段另需成立的前提）、SP 與綁定如預期、沒有外部干擾，第二次仍返回 255，不會因第一次排程失敗而釋出一個 task 槽。不能將這份短路寫址清單套到排程通過而配置節點的路徑。

更一般地，若兩次登記之間只有首次成功登記本身改計數，兩次均滿表／僅首次成功／兩次成功的分界分別是 `n>=c`、`c-n==1`、`c-n>=2`。特別是首次拿到合法 ID 254 時，容量必為 255；第二次必滿。名義 `n=3,c=29` 則依序得到 3、4。這是參考映像的條件結果，不是實機記錄。

重現（decoded APP、V1.31 主段）：解出短路路徑兩個 frame 的保存位移，核對兩個服務槽、分支與填值參數，再列舉初始計數／容量。映射與填值函式本體的交叉檢查見上方連結。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('full-to-second mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def val(buf,i,n): return int.from_bytes(buf[i:i+n],'little')
def saves(buf,sites):
    out=[]
    for i in sites:
        h=val(buf,i,2); ck(h&0xe003==0xc002); out.append(4*(h>>9&15)+64*(h>>7&3))
    return sorted(out)
ck(saves(b,[0x372a,0x372c,*range(0x3732,0x3740,2)])==list(range(12,48,4)) and saves(a,[0x107c,0x1084])==[8,12])
ck(b[0x3750:0x3758].hex()=='83c7d7196378f500' and b[0x3764:0x376e].hex()=='b747024023a6472199a0')
ck((val(b,72,4),val(b,128,4))==(0x2000039c,0x43c4e))
d=0x908c+(val(a,0x108c,4)&0xfffff000)+(val(a,0x1090,4)>>20^2048)-2048; size=val(a,0x1086,4)>>20; ck((d,size)==(0x2000be08,180))
e=0x2000ffc0; ck(all(p+k<=0x2000319d or p>=0x2000319f for p,k in [(e-36,36),(e-8,8),(d,size),(0x4002420c,4)]))
def reg(n,c): return (255,n) if n>=c else (n,n+1)
hist=[0,0,0]
for c in range(256):
    for n in range(256):
        first,m=reg(n,c); second,last=reg(m,c); k=last-n
        ck(k==min(2,max(c-n,0)) and (first!=255)+(second!=255)==k); hist[k]+=1
ck(hist==[32896,255,32385]); print('PASS: 11 stack stores; 65536 pairs: neither 32896, first only 255, both 32385')
```
