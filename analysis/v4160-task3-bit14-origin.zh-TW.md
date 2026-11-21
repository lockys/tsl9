# Task 3 的 0x4000：找到續排，未識別首次設位者

原 APP `0x1995c` 每次只選一個已知事件：優先順序是 `0x8000`、`0x0001`、`0x2000`、`0x4000`。對遮罩 `0x6000`，本次處理 `0x2000`，正常返回 `0x4000`。若返回遮罩未被取消、仍合併到同一 task，下一次派送此 task 且沒有更高優先位時才處理 `0x4000`；不是在同一次呼叫連跑兩支。若有新高優先事件，不能保證下一次就輪到它。

`0x199c2` 檢查入口 a1 的 bit 14。若選中，`0x199dc` 經 `[0x40058]` 要求 `(U8[gp+388],0x4000,1600)`；沒有 `0x2000` 路徑的兩次校準前置呼叫。正常返回且 s0 保持時，APP 不看排程結果，回傳原遮罩 XOR `0x4000`。因此此處**依賴先收到該位**，不能用它解釋第一次。`0x19b54` 的已知初始排程設的是 `0x2000`，不會憑空產生 bit 14；返回合併也只保留或合併事件，不會從 `0x2000` 推出 `0x4000`。

為找其他直接來源，逐半字掃描整個 decoded APP 的 `lui a1,4` 和 `c.lui a1,4`。只有兩處：上述續排，及 `0x121f2`。後者在任何呼叫之前就於 `0x12204` 將 a1 加 257，成為 `0x4101`，在 `0x12232` 用於比較，不是直接排入 `0x4000`。**此掃描不能排除**由別的暫存器搬入、複合遮罩、資料表、間接回呼或 resident 發出的首次事件。未把「未找到」當成不可達。

重現：以下 Python 接受 decoded APP 路徑，核對上述立即數和呼叫窗口，並比較移位判斷與位元優先序；不需要連接設備。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('bit14 evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(p,n): return b[p-32768:p-32768+n]
ck([i+32768 for i in range(0,len(b)-1,2) if b[i:i+2]==bytes.fromhex('9165') or b[i:i+4]==bytes.fromhex('b7450000')]==[0x121f2,0x199d6])
ck(raw(0x12204,4).hex()=='93851510' and raw(0x12232,4).hex()=='6312b704')
ck(raw(0x199cc,22).hex()=='b7070400bc4f13060064916503c541188297116545b7' and raw(0x19b50,6).hex()=='896541010283')
def shift(pc): return int.from_bytes(raw(pc,4),'little')>>20&31
s=[shift(p) for p in (0x1995e,0x19996,0x199c2)]; ck(s==[16,18,17]); counts=[0]*4
for m in range(65536):
    sign=lambda n: bool((m<<n)&0x80000000)
    i=0 if sign(s[0]) else 1 if m&1 else 2 if sign(s[1]) else 3 if sign(s[2]) else 4
    ck(i==next((k for k,bit in enumerate((32768,1,8192,16384)) if m&bit),4))
    if m&0x6000==0x6000: counts[i]+=1
ck(counts==[8192,4096,4096,0]); print('PASS: 65536 masks; both-bit classes',counts,'; 2 literal sites')
```
