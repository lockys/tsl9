# 兩個上游入口的 selector：同一個呼叫點可收到不同常數

[前次](v4160-setup-event-selector.zh-TW.md)未能單憑 a3=0 判定索引。本次由 v4.1.60 APP 呼叫者追 a0，不假設全域 ABI 會自動截成 byte。

* **經 `0x12abe → 0x12acc`：** 零走另一服務，非零原樣進 `0x16cc4`。`0x12b76` 傳 1；`0x1489a/a4/ae` 依次傳 0、1、2。`0x12d2c` 用 LBU 從當下 `sp+19` 讀入，所以完整 a0 在 0..255。`0x12d46` 則依**重讀**的該 byte 是否等於 2 而傳 1 或 2，不假設前後值相等。上述路徑即使 byte 的值未知，能通過 `0x16cc4` 入口檢查的完整值也只有 1、2。
* **經 `0x12aa0 → 0x16dac → 0x16dc8`：** `0x12b36/3c` 前分別傳 1、2；`0x144b0/b6/bc` 前傳 0、1、2。`0x1481a` 循序到達時為 1，但 `0x14836` 可帶 0 跳入；`0x14820` 循序到達時為 2，但 `0x14846` 可帶 1 跳入。`0x14840` 前傳 0。`0x12aa0` 在呼叫 `0x1070a` 前把 a0 存到棧上，返回後**重讀保存的 word**；只有它仍等於原值且非零，才可把上述常數一路帶到 `0x16dc8`。不能只依呼叫指令前一條 `li`，也不能把保存槽未變當成已證事實。

結論限上述路徑及中途正常返回、保存值未變：進入 helper 時的索引 1、2 仍選事件遮罩 2、4，不會補送事件 1。這不是所有間接入口或裝置行為的證明。可重播核對（repo 根目錄，Python）：

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('upstream selector mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n],'little')
def li(p):
    h=u(p,2); ck(h&0xff83==0x4501); return ((h>>2&31)|(h>>7&32))
edges=[]; jumps=[]
for p in range(32768,32768+len(b)-3,2):
    w=u(p,4); h=w&65535
    d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    t=p+(d^1048576)-1048576
    if w&127==111 and t in (0x12abe,0x12aa0,0x16dac): edges.append((p,t,w>>7&31))
    if h&0xe003==0xa001:
        v=sum((h>>s&1)<<j for s,j in zip((12,11,10,9,8,7,6,5,4,3,2),(11,4,9,8,10,6,7,3,2,1,5)))
        t=p+(v^2048)-2048
        if t in (0x1481a,0x14820): jumps.append((p,t,li(p-2)))
ck([p for p,t,d in edges if t==0x12abe and d==1]==[0x12b76,0x12d2c,0x12d46,0x1489a,0x148a4,0x148ae])
ps=[p for p,t,d in edges if t==0x12aa0 and d==1]; ck(ps==[0x12b36,0x12b3c,0x144b0,0x144b6,0x144bc,0x1481a,0x14820,0x14840]); ck([li(p-2) for p in ps]==[1,2,0,1,2,1,2,0])
ck(len(edges)==15 and (0x12aba,0x16dac,0) in edges and jumps==[(0x14836,0x1481a,0),(0x14846,0x14820,1)])
ck([li(p) for p in (0x12b70,0x14898,0x148a2,0x148ac,0x12d3a,0x12d40)]==[1,0,1,2,1,2]); ck(u(0x12d20,4)==0x01314503 and u(0x12d30,4)==0x01314703 and u(0x12d3c,4)==0x00f70363)
ck(u(0x12aa2,2)==0xc62a and u(0x12aaa,2)==0x4532); ck({x for x in range(256) if x and ((x-1)&255)<=1}=={1,2})
print('PASS: 15 JAL edges, 2 alternate short jumps, 256 byte selectors')
```
