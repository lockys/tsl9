# 首次計時節點：成功後哪些寫入能排除？

接續[首次小塊配置](v4160-first-timer-block.zh-TW.md)與[排程返回](v4160-role-tail-s0-slot.zh-TW.md)。本次只看配置已返回、`a0=P=0x200043b4`、重新讀到空表頭的分支。V1.31 的兩條短 byte store 採 Xwchc 解讀。入口 `E=0x2000ffc0` 時，排程器保存的 s0、ra 分別佔 `[E-8,E-4)`、`[E-4,E)`。

|寫入次序（PC）|目的地與寬度|
|---|---|
|`43850`|表頭 `0x200031e8`，4 bytes|
|`43856,4385a,4385c`|依序 `P+12`（4）、`P+8`（4）、`P+2`（2）|
|`43860,43862,43864`|依序 `P+0`（1）、`P+1`（1）、`P+4`（4）|
|`43818`|跳回共同成功出口後寫外設 `0x4002420c`，4 bytes；這是 CPU 目的地址，非外設副作用的模型。|

六次節點寫入恰好覆蓋 `[0x200043b4,0x200043c4)`，每個 byte 一次；與兩個保存 word 不相交。**不必知道期限或時鐘樣本的值**才能做這項判斷。若配置後重讀到非空表頭，掛鏈寫入改為舊尾節點的 `+12`，不是固定表頭：不能直接套用空表的結論。查找命中時也不走本次配置分支。這項結果不包含配置器內部、不證明未知回呼正常返回，也不增加已重建 BIN 的 byte 數。

重現：傳入 V1.31 carrier。下列檢查固定該分支位元組，依上述指令解讀檢查寫入寬度、完整欄位覆蓋與保存區間。以縮短 `P+2` 欄位的負對照確認覆蓋檢查能發現遺漏。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('first node footprint mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def window(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
window(0x43846,'373700208327871e99ef2324a71e85472326050004c52311550100a11cb12322050075b7')
window(0x43814,'b747024023a64721054559bf');window(0x43732,'06d622d4');window(0x437b4,'b2502254')
p,e=0x200043ac+8,0x2000ffc0
fields=[(12,4),(8,4),(2,2),(0,1),(1,1),(4,4)]
def covered(fs):return sorted(i for off,n in fs for i in range(off,off+n))==list(range(16))
ck(covered(fields) and not covered(fields[:2]+[(2,1)]+fields[3:]))
writes=[(0x200031e8,4)]+[(p+off,n) for off,n in fields]+[(0x4002420c,4)]
ck(all(a+n<=s or s+4<=a for a,n in writes for s in (e-8,e-4)))
print(f'PASS: {len(writes)} stores, 16 node bytes exactly once, 2 saved words disjoint; node-to-frame-slot gap {(e-8)-(p+16)} bytes')
```
