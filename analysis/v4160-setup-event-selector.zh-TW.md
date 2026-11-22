# 同一任務 ID 不代表同一個事件：0x16858 的兩個呼叫點

接續[初始化送出事件 1](v4160-setup-initial-post.zh-TW.md)。沿設定 handler 已知的 selector **1、2** 路徑，`0x16858` 分別讀到遮罩 **2、4**，不是 1。以參數 1 呼叫並不等於發送事件 1。

|直接進入 `0x16858` 的指令|索引 a0|動作選擇 a1|
|---|---|---|
|`0x16c8a`|`0x16c72` 的入口 a0 原值|固定 0，尾跳槽 `0x4005c`|
|`0x16d92`|`0x16cc4` 的入口 a0 先存 s0，再傳回 a0|入口 a3 先存 s3，再傳入 a1；0 用 `0x4005c`，非零用 `0x4022c`，後者另傳 1600|

第二條需中間呼叫正常返回並保存 s0、s3。兩個入口的檢查都是 `((a0-1)&255)<=1`；遮罩檢查的是低 byte，**並未把傳入的完整索引縮成 byte**。所以不能僅憑門檻宣稱所有呼叫都索引 1 或 2。已知的 `0x16f00` handler 分支以完整常數 1 或 2 進 `0x16dd4`，再以 a3=1 呼叫 `0x16cc4`；這條鏈才有完整索引的來源。另兩處 `0x12acc`、`0x16dc8` 進 `0x16cc4` 前設 a3=0，不能據此倒推 a0。

`0x16858` 建立小端半字表 `{0,2,4}`，以完整索引選取半字，另讀 `gp+363` 作目的 ID。V1.31 參考槽分別指向 `0x439a8` 和 `0x43932`。上述兩個固定 selector 不會經這個 helper 傳入遮罩 1；不排除其他事件來源，也不證成功排程、實機 ROM 或所有間接呼叫。

以下從 repo 根目錄執行，掃描原 BIN 的半字對齊 JAL，核對固定呼叫段與兩個 slot，並由原指令立即數重建表。測試不是整機執行。

```python
from hashlib import sha256
from pathlib import Path
def ck(v):
    if not v: raise ValueError('selector evidence mismatch')
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-32768:p-32768+n]
def pin(p,h): ck(raw(p,len(bytes.fromhex(h)))==bytes.fromhex(h))
def word(p): return int.from_bytes(raw(p,4),'little')
edges=[]
for pc in range(32768,32768+len(b)-3,2):
    w=word(pc); d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    t=pc+(d^1048576)-1048576
    if w&127==111 and t in (0x16858,0x16cc4): edges.append((pc,t,w>>7&31))
ck(edges==[(0x12acc,0x16cc4,0),(0x16c8a,0x16858,1),(0x16d92,0x16858,1),(0x16dc8,0x16cc4,1),(0x16df2,0x16cc4,1)])
for p in (0x16c72,0x16cc4): pin(p,'9307f5ff93f7f70f0547')
pin(0x16c82,'814506c622c42a84'); pin(0x16cf0,'2a8481454808b689'); pin(0x16d8e,'ce852285'); pin(0x16dec,'2c0085462146'); pin(0x12aca,'8146'); pin(0x16dbe,'8146')
pin(0x1685a,'b70702003ec4914718082316f10006053a95'); pin(0x16874,'91c9835585ff0323c722130600643e8541010283835585ff0323c7053e8541010283')
stack=(word(0x1685a)&0xfffff000).to_bytes(4,'little')+((word(0x16860)>>2)&31).to_bytes(2,'little')
ck([int.from_bytes(stack[i:i+2],'little') for i in (0,2,4)]==[0,2,4])
ck([int.from_bytes(r[i:i+4],'little') for i in (92,556)]==[0x439a8,0x43932])
ck([v for v in range(256) if ((v-1)&255)<=1]==[1,2])
print('PASS: 5 direct edges; 256 low-byte decisions; fixed selectors 1/2 select masks 2/4')
```
