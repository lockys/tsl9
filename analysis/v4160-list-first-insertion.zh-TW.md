# 空串列的首次插入不走前驅寫入

接續[容量的寬寫入](v4160-capacity-wide-init.zh-TW.md)。以下只解讀 V1.31 參考映像，不假定實機載入。令 B=`0x200033b8`，串列頭為 B+204 (`0x20003484`)，與上次追查的容量 B+63 不同。

* 啟動清零包含整個 head word。另有明確初始化 `0x5e758`：先清 B+200 的 byte，再清 B+204 的 word，之後才尾跳。這段存在不代表它在首次角色讀取前另執行了一次。
* `0x5e5d2` 讀 head，`0x5e5e2` 令前驅 s4=0。若 head=0，`0x5e5ee` 不走訪，直接以 64、594 呼叫配置函式；若配置失敗則返回。成功且中途呼叫正常返回、維持相應暫存器時，`0x5e6a4` 不跳：`0x5e6a8` 發布新 head，`0x5e6ac` 才清新節點的 next（+60）。所以這次空表插入不執行 `0x5e700`，且不是「先清 next 再發布」。不對非同步讀者或其他寫入作推論。
* 找到直接呼叫 `0x68a14`，參數是 sp+4。它的上游 `0x689be` 讀 B+200、B+201 兩個 byte。只有 **B[200] < B[201]** 且 **word[B+216] 的 bit 6 為 1** 才通過這兩道檢查；否則分別帶 7、18 到 `0x68a22` 返回。這只是必要條件。這裡的上限是 `0x20003481`，不能與 `0x200033f7` 混用。兩道檢查涉及的儲存格都在啟動清零範圍；若這些值未更新，此呼叫不會發生。

因此不必先假定首次插入的配置地址才能排除該次前驅寫入。不能據此排除預先存在的串列、另一個呼叫者或後續插入。下一個時序問題是首次角色讀取前，B+201 與 B+216 是否已被設定。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('list insertion evidence mismatch')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x5e758,'b73700209387873b2384070c23a6070c6f500f90');raw(0x5e5c8,'373900209307893b22cc03a4c70c');raw(0x5e5e2,'014a1309893b93094500854a65e093052025130500049720fa1fe78080a42a841d4545cc');raw(0x5e6a4,'631e0a042326890c232e0402');raw(0x5e700,'232e8a0265b7');raw(0x6897a,'b73700202a871385873b034815009387873b');raw(0x689be,'83c8870c03c8970c1d4563fd080583a7870d494593f70704b1c7');raw(0x68a12,'4800ef501fbb');raw(0x68a22,'8280')
w=int.from_bytes(b[0x28a14:0x28a18],'little');d=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1;ck(w&4095==239 and 0x68a14+(d^0x100000)-0x100000==0x5e5c4)
B=0x200033b8;ck(0x20002ef8<=B+200<B+220<=0x20003618 and B+204==0x20003484);counts=[sum(n<c and bool(mask&64) for n in range(256) for c in range(256)) for mask in (0,64)];ck(counts==[0,32640]);print('PASS: empty-head branch and stores; direct caller; 131072 gate combinations')
```
