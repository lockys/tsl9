# `0x44090` 重讀的是否還是配置器返回的 P？

須分開證明兩件事：載入用的基底暫存器 `s1` 不變，以及該 RAM word 的內容不變。`0x44076` 將配置返回值 P 存到 `0x200031bc`；`0x44078` 設 `s1=0x2000319c`。`0x44090` 每次從 `s1+32` 讀 a2，`0x440bc` 是寫 `[a2]`，**不是**寫 `[s1+32]`。

* 第一輪：若 P 在名義 arena，依[填值範圍](v4160-44086-task-base-fill-bound.zh-TW.md)，填值地址自 P 向上且不回繞，另寫一個外設 word；均不碰 `0x200031bc`，該 helper 也不寫 s1。故正常返回且無其他寫入時，首次載入得 P。
* 由一輪推至下一輪：若本輪載入 P，位於 arena 的 `[P,P+4)` 不碰保存 P 的 word。當 `cfg+60` 綁定原 APP `0x197be`，核對它和五個子函式的整段指令，沒有一條以 s1 或 s2 為目的暫存器。這不靠「依 ABI 應保存」猜測。按[回呼寫址清單](v4160-cfg60-heap-separation.zh-TW.md)及[名義堆疊](v4160-cfg60-init-stack.zh-TW.md)，原設定的三輪回呼也不直接寫該 RAM word。若各輪正常返回、設定及映射維持且無外部干擾，下一輪重讀仍得 P；退出時 `0x44096` 傳給釋放函式的也是 P。
* **停止點：**交出相同 P 不等於釋放後串列一定有效。這不是每種設定或裝置的保證，也不保證外設輪詢必定退出。

重現（參數依序為 decoded APP、V1.31 主段）。檢查針對固定來源的指令類別與目的暫存器，不是 CPU 模擬；寫址和 stack 條件見上列兩份分析。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('reload evidence mismatch')
ck([sha256(v).hexdigest() for v in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(b[0x4072:0x407c].hex()=='1387c41908d39384c419' and b[0x4090:0x4098].hex()=='9050634df9003285' and b[0x40bc:0x40c2].hex()=='08c20297f9b7')
count=0; callees=[]
for p,end in [(0x197be,0x197f0),(0x19764,0x1979a),(0x18e98,0x18eb6),(0x18eb6,0x18ec4),(0x18ec4,0x18ef2),(0x18ef2,0x18f56)]:
    while p<end:
        w=int.from_bytes(a[p-0x8000:p-0x8000+4],'little'); h=w&65535; q=h&3; f=h>>13; rd=None
        if q==3:
            op=w&127; ck(op in (3,19,35,51,55,99,111))
            if op not in (35,99): rd=w>>7&31
            if op==111:
                off=(w>>31<<20)|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1
                ck(rd==1); callees.append(p+(off^1048576)-1048576)
        elif q==0 and f==2: rd=8+(h>>2&7)
        elif q==1 and f==4: rd=8+(h>>7&7)
        elif (q,f) in [(1,0),(1,2),(1,3),(2,2)]: rd=h>>7&31
        elif q==2 and f==4 and h!=0x8082:
            ck(not(h&0x1000) and h>>2&31); rd=h>>7&31
        else: ck((q,f) in [(0,6),(1,6),(1,7),(2,6)] or h==0x8082)
        ck(rd not in (9,18)); p+=4 if q==3 else 2; count+=1
    ck(p==end)
ck(callees==[0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764])
print('PASS:',count,'instructions; 5 direct calls; no s1/s2 destination')
```
