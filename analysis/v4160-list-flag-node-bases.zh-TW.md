# 另外兩筆 +216 寫入是節點欄位，不是固定旗標

在 V1.31 參考映像，`0x536d2` 的固定目的位址為 `0x20003490`，但不能把另外兩個同位移的 store 也算成初始化寫入。令 `P` 為 `0x5784a` 的傳回值。

|路徑|基址來源|走到 +216 分支的必要條件之一|
|---|---|---|
|`0x67394 → 0x6872e`|`0x6873e` 呼叫查找，`0x68746` 把 P 放進 s1；其後有一次 helper 呼叫，須正常返回且保持 s1。|`P != 0` 且 `byte[P+76] == 0` 才由 `0x68784` 跳到 `0x687ee`，末端 `0x6883a` 寫 `word[P+216]`。|
|`0x673b0 → 0x68844`|`0x6884a` 呼叫同一查找，`0x68854` 把 P 放進 a5。|`P != 0` 且 `byte[P+77] == 0` 才由 `0x68882` 跳到 `0x688de`，末端 `0x68926` 寫 `word[P+216]`。|

查找讀的是**另一條串列**的頭 `0x20003454`，不是 `0x20003484`。空頭傳回零；候選 Xwchc 解讀下，命中時返回目前節點，未命中則沿節點首 word 前進。兩個 store 的起始地址要等於 `0x20003490`，節點 P 必須恰為 `0x200033b8`。若這條串列為空，兩處都不到；若全由[已辨認的 488-byte 配置路徑](v4160-lookup-head-first-writer.zh-TW.md)建立，且節點均落在正常 arena（payload 起點至少 `0x200043b4`），兩處即使執行也不會覆蓋該旗標。

這是對寫入目的的條件排除，並非以位址大小推斷執行先後。兩個直接呼叫編碼存在，不證它們早於首次角色讀取，也不證所有節點的來源。兩處均寫整個 word，不是固定設 bit 6 的指令。

以 V1.31 carrier 為參數核對：

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes();base=0x40000
def ck(v):
    if not v:raise ValueError('list flag node evidence mismatch')
def raw(p,h):
    a=bytes.fromhex(h);ck(b[p-base:p-base+len(a)]==a)
def w(p):return int.from_bytes(b[p-base:p-base+4],'little')
def jal(p):
    x=w(p);ck(x&4095==239);v=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;return p+(v^0x100000)-0x100000
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');ck([jal(p) for p in (0x67394,0x673b0,0x6873e,0x6884a)]==[0x6872e,0x68844,0x5784a,0x5784a]);raw(0x5784a,'b737002083a7474599e33e8582809a27e30da7fe9c43cdbf');raw(0x68742,'7dcd3c35aa84');raw(0x68774,'03c5c404');raw(0x68784,'2dc5');raw(0x6884e,'79cd34350547aa87');raw(0x6887e,'83c6d704b1ce')
for p,r in [(0x6883a,9),(0x68926,15)]:
    x=w(p);ck(x&0x707f==0x2023 and x>>15&31==r and ((x>>25<<5)|(x>>7&31))==216)
ck(0x20003000+(w(0x5784e)>>20)==0x20003454 and 0x20003490-216==0x200033b8<0x200043b4);print('PASS: 4 call edges, separate lookup head, 2 node-relative word stores')
```
