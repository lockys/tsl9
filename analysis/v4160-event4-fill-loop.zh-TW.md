# V1.31 參考填充迴圈：三個 bytes 之後停在哪裡？

承接[七個 APP 請求](v4160-event4-init-bulk.zh-TW.md)。在 V1.31 參考檔，槽 `0x40048` 指向 `0x2000039c`；以下採用啟動時已將 carrier `0x4060c` 起的程式複製至該 RAM 位址的條件。

`0x200003ac` 遇空目的直接進還原段；否則以 32-bit 加法形成結尾 `D+n`，長度零亦不進迴圈。非空且非零時，`0x200003be` **先加一**，`0x200003c0` 再以 **−1** 位移寫一個 byte，因此第一次寫的是 D，不是 D+1。`0x200003c4` 比較加一後的指標和結尾，相等就退出。三位元組請求的最後寫址是 `gp+362`，比較時指標雖已是 `gp+363`，**並未向該位址寫入**。

函式並非只寫目的緩衝區：迴圈前讀外設 word `0x4002420c` 並寫零，離開時把先前讀值寫回同址。連空目的及零長度路徑亦有這兩筆 word store；不據此推斷外設內部狀態完全還原。沒有實機 ROM 身分、無中斷或存取一定成功的證據。

以下是固定指令窗的有限控制流重播，不是完整 CPU。參數為 V1.31 carrier；以獨立產生的預期位址序列核對全部七組，另檢查空目的、零長度與跨 32-bit 結尾。檢查的是架構層的 store 位址、寬度和資料，不模擬 MMIO 效應。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('unexpected fill evidence')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[72:76]==bytes.fromhex('9c030020'))
ops='37470240 8327c720 23260720 0f100000 01c5 3307c500 11e6 37470240 2326f720 8280 0505 a30fb5fe e31de5fe f5b7'.split()
stream=b[0x60c:0x63a]; ck(stream==bytes.fromhex(''.join(ops)))
mask=0xffffffff; io=0x4002420c; sample=0xa7c31450

def run(d,n,v):
    a=d; pc=0; writes=[]; budget=20+4*n
    while budget:
        budget-=1
        if pc in (0,24): h=0x40024000
        elif pc==4: ck(h+524==io); saved=sample
        elif pc==8: writes.append((h+524,4,0))
        elif pc==12: pass  # fence.i, no data store
        elif pc==16 and a==0: pc=24; continue
        elif pc==18: h=(a+n)&mask
        elif pc==22 and n!=0: pc=34; continue
        elif pc==28: writes.append((h+524,4,saved))
        elif pc==32: return writes
        elif pc==34: a=(a+1)&mask
        elif pc==36: writes.append(((a-1)&mask,1,v&255))
        elif pc==40 and a!=h: pc=34; continue
        elif pc==44: pc=24; continue
        pc+=4 if stream[pc]&3==3 else 2
    raise ValueError('step budget')

g=0x20004000; ids=[g+i for i in (148,152,166,363)]
rows=[(0x2000b18c,2124),(0x2000be08,180),(0x2000bfd4,24),(0x2000bfec,36),(0x2000c7a0,268),(g+144,3),(g+360,3)]
for i,(d,n) in enumerate(rows+[(0,3),(g,0),(mask-1,3)]):
    v=0 if i<7 else 0x123
    seq=run(d,n,v); expected=[((d+j)&mask,1,v&255) for j in range(n) if d]
    ck(seq==[(io,4,0)]+expected+[(io,4,sample)])
    if i<7: ck(all(not any(p<=x<p+k for x in ids) for p,k,_ in seq))
print('PASS: 7 APP ranges, 2638 byte stores, 14 peripheral word stores; 3 boundary cases')
```
