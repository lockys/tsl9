# 首次 APP 登記的 255 會到哪裡？

在 v4.1.60 APP，`19b34` 將登記結果低 byte 存在 `gp+388`。`19b38` 呼叫 `19b56`，返回後 `19b3a` 用 `lbu` 從 s0 所指的 byte **重讀**，並非使用該呼叫的回傳值。至 `19b54` 尾跳前沒有比較 ID；事件與延遲仍為 `0x2000`、192000。故在[校時正常返回且該 byte 與指標保持](v4160-task-clock-copy16.zh-TW.md)時，成功 ID 與滿表值 255 走的是同一段 APP 指令。

差別發生在 V1.31 參考排程器。若登記成功的舊計數為 n，登記後計數保持 n+1，第一道 `ID < count` 檢查必過，**即使 n=0**；通過不是建立計時器的保證。若登記滿表，保存並讀回的值為 255，則即使計數在此期間變成任何其他 byte，也**不可能**通過。`43754` 跳到 `43764`，略過時鐘槽載入，恢復控制 word 後返回 0，不查找或配置計時節點。這不是整個呼叫沒有副作用。[返回 APP 後](v4160-first-schedule-return-contract.zh-TW.md)不依這個 0 中止初始化。

重現：依序傳入 decoded APP 與 V1.31 主段；核對原始片段，從兩條 BGEU 各自取操作數及目的位址。下列是兩個分支的組合，不是整機重播。若 `19b3a` 讀到別的值，必須改用當時的 ID，不能再套用 255 的結論。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('first ID flow mismatch')
ck([sha256(v).hexdigest() for v in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(a[0x11b30:0x11b56].hex()=='138441182300a400392803450400224403a38405b240924437f60200130606e0896541010283')
ck(b[0x3750:0x3754].hex()=='83c7d719' and b[0x3764:0x376e].hex()=='b747024023a6472199a0' and b[0x37b2:0x37b4].hex()=='0145')
def bgeu(pc,target):
    i=pc-0x40000; w=int.from_bytes(b[i:i+4],'little'); ck(w&0x707f==0x7063)
    d=(w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1; ck(pc+(d^4096)-4096==target)
    l,r=w>>15&31,w>>20&31; return lambda regs:regs[l]>=regs[r]
full=bgeu(0x43c5a,0x43c78); reject=bgeu(0x43754,0x43764); passed=0
for n in range(256):
    for c in range(256):
        f=full({15:n,13:c}); ident,count=(255,n) if f else (n,n+1)
        ck(f==(n>=c) and reject({10:ident,15:count})==f); passed+=not f
ck(passed==32640 and all(reject({10:255,15:k}) for k in range(256)))
print('PASS: 32640 success pairs pass ID gate; 32896 full pairs rejected; 255 rejected for every live byte count')
```
