# 四個寫入服務呼叫點，三個入口框架（V1.31 參考映像）

沿[先前找到的呼叫點](v4160-ingress-resident-call-frame.zh-TW.md)往上查。設 `U` 為下列各自入口的堆疊指標，`E` 為被呼叫的 `0x4bb22` 的入口堆疊指標。假設從候選入口執行、子呼叫正常還原 SP 且沒有切換堆疊：

|候選入口|呼叫 `0x4bb22` 的位置|E|該框架還原 SP / ret|
|---|---|---|---|
|`0x4bbc6`|`0x4bc20`、`0x4bc92`|`U−48`|`0x4bc54 / 0x4bc56`|
|`0x4bcbc`|`0x4bcce`|`U−32`|`0x4bcd4 / 0x4bcd6`|
|`0x4bdc6`|`0x4be02`|`U−48`|`0x4be24 / 0x4be26`|

第一列不能依檔案順序在第一個 `ret` 處截斷：`0x4bc10` 的條件分支可越過它到 `0x4bc62`，再經 `0x4bc6e` 的迴圈分支到 `0x4bc92`；不跳時則可落到 `0x4bc20`。第二列有自己的 32-byte prologue，而且 `0x4bccc` 保存 ra，`0x4bcd2` 取回。以上是條件控制流，不表示四處在同一輪執行、同一個 U 值，或有四層堆疊。上層 U 和實機 resident 版本均未證實。

重現：傳入 V1.31 主連續區段 BIN。檢查入口/出口、四個 JAL，以及越過第一個 ret 的壓縮分支。

```python
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('unexpected frame evidence')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(p,n): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
for start,end,enter,leave,calls in [(0x4bbc6,0x4bc54,0x7179,0x6145,[0x4bc20,0x4bc92]),(0x4bcbc,0x4bcd4,0x1101,0x6105,[0x4bcce]),(0x4bdc6,0x4be24,0x7179,0x6145,[0x4be02])]:
    ck(word(start,2)==enter and word(end,2)==leave and word(end+2,2)==0x8082)
    for pc in calls:
        w=word(pc,4); d=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
        ck(w&4095==0xef and pc+((d^0x100000)-0x100000)==0x4bb22)
h=word(0x4bc10,2); d=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
ck(h&0xe383==0xc101 and 0x4bc10+((d^256)-256)==0x4bc62)
ck(word(0x4bccc,2)==0xce06 and word(0x4bcd2,2)==0x40f2)
print('PASS: 4 JAL sites, 3 paired frames (48/32/48), branch over first return')
```
