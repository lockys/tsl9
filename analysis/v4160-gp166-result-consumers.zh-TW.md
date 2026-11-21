# `0x90a8` 的登記結果由誰讀取？

原 APP `90a2` 以 handler `901a` 呼叫登記槽；`90a8` 不比較結果，只將 a0 低 byte 存到 `gp+166`（名義 GP `0x20004000` 時是 `0x200040a6`）。這不是上一個排程呼叫的成功旗標，也不是 `gp+388` 的第一個 APP task ID。四處直接讀取均為 `lbu a0,166(gp)`，也就是取**當時的 byte 作下一次服務呼叫的第一參數**，並非在 APP 端測試真假。

|讀取 PC|到達條件與消費方式（以表基址 `0x40000` 計）|
|---|---|
|`90f2`|`90b0` 找到匹配記錄，必要時先呼叫 `[40068]`。重讀 ID 後清除記錄的 +4、+8，以 ID 與索引位元遮罩尾跳 `[4005c]`。|
|`9178`|`9124` 的零延遲快速路徑找到空記錄並填入，再以 ID、遮罩尾跳 `[40050]`。|
|`91be`|一般路徑找到匹配記錄，必要時先呼叫 `[40068]`，然後讀 ID、更新記錄。|
|`9226`|一般路徑未匹配但找到空記錄，先填入再讀 ID；`922a` 跳到 `91d0`，與上列共用出口。|

後兩路在 `91e8` 測的是**當時完整的 s0 模式值，不是 a0 的 ID**：非零尾跳 `[4022c]`；零則呼叫 `[40058]`，再對服務回傳值做 `seqz`。每次選中的記錄索引決定 a1 的低 16 位遮罩，與登記結果分開。相反，已登記的 handler `901a` 直接掃傳入 a1 的低 15 個位元，不靠重讀 `gp+166` 選記錄。四處不代表執行順序或呼叫次數。讀到的 ID 等於初始化結果仍以 GP 穩定、期間無覆寫為前提；即使讀到 255，這四段也不在呼叫前單獨拒絕它。

重現：傳入原 decoded BIN。對所有半字對齊視窗掃標準 RV32 整數 load/store，含寬存取覆蓋目標 byte 的情形。這不是所有指標別名、間接存取或可達性證明。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('gp166 evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
hits=[]
for i in range(0,len(b)-3,2):
    x=int.from_bytes(b[i:i+4],'little'); op=x&127; k=x>>12&7
    if op not in (3,35) or (x>>15&31)!=3: continue
    widths={0:1,1:2,2:4,4:1,5:2} if op==3 else {0:1,1:2,2:4}
    d=x>>20 if op==3 else ((x>>25<<5)|(x>>7&31)); d=(d^2048)-2048
    if d<=166<d+widths.get(k,0): hits.append((0x8000+i,x))
ck(hits==[(0x90a8,0x0aa18323)]+[(p,0x0a61c503) for p in (0x90f2,0x9178,0x91be,0x9226)])
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x8000:p-0x8000+len(v)]==v)
raw(0x9106,'03a3c705924441010283');raw(0x9174,'03a3070503c5610a05610283');raw(0x91e4,'b707040031c0');raw(0x91f6,'03a3c72205610283');raw(0x922a,'5db7bc4f829713351500')
print('PASS: 38399 aligned windows; 1 direct byte store, 4 unsigned byte loads into a0; 4 service-slot offsets')
```
