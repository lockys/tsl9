# 可選校準回呼：設定本體與保存指標是兩個不同的寫入目標

以 `C` 表示 APP 傳給 `[0x40074]` 的 16-byte 設定位址，也是呼叫當下的 SP。V1.31 參考 `0x43f46` 將 SP 降到 `C−32`，先 `a1=a0`。回呼槽為零時，`0x43f5c` 跳 `0x43f64`，**不**保存或重載指標。非零時 `0x43f5e` 把 a0（即 C）存到 `[C−20,C−16)`，`0x43f60` 呼叫之後，`0x43f62` 從同一格重載 a1。重載的是指標，不是設定內容。

若槽仍是[初始化提供的 `0x197b8`](v4160-task-clock-callback-origin.zh-TW.md)，此 wrapper 以 `a0=3` 進入校準，不把傳進來的 C 當寫入目的。回呼比[直接呼叫校準](v4160-calibration-store-footprint.zh-TW.md)多一層 32-byte frame：此時校準 SP 是 `C−112`，其 14 個 stack store 合計只可能寫 `[C−100,C−96)` 與 `[C−84,C−32)`；其餘直接 store 在四個已核對的 MMIO 位址。取 `C=0x2000ff90` 時，保存指標在 `0x2000ff7c`，設定第四欄在 `0x2000ff9c`。校準兩段 stack 寫入都不到這兩處，也不到設定其餘三欄。

所以在正常返回、名義堆疊、無外部改寫／映射別名的條件下，這次回呼不會直接改掉保存指標或清零的第四欄。若槽被改成其他函式，這個結論不能沿用；重新載入 a1 本身不保證指標或資料未變。此處未證槽從初始化至首次校時一直相同，也不證裝置使用該參考 ROM。

重現：將 decoded APP 與 V1.31 參考 carrier 依序傳入。逐指令取長度、解出校準的壓縮 stack stores，並核對嵌套時的 byte 集合；MMIO 基址及目標函式身分見上方兩份報告。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('clock hook evidence mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x3f46:0x3f64].hex()=='011122cc373400209307c41e9c5b06ceaa851304c41e81c72ac68297b245')
ck(a[0x1129a:0x1129c].hex()=='5d71' and a[0x117b8:0x117be].hex()=='0d456ff01fae')
c=0x2000ff90; frame=c-32-80; pos=0x1129a; stores=[]
while pos<0x116c4:
    h=int.from_bytes(a[pos:pos+2],'little'); size=4 if h&3==3 else 2
    if h&0xe003==0xc002: stores.append(frame+4*(h>>9&15)+64*(h>>7&3))
    pos+=size
written={s+i for s in stores for i in range(4)}
ck(pos==0x116c4 and len(stores)==14 and written==set(range(c-100,c-96))|set(range(c-84,c-32)))
ck(written.isdisjoint(range(c-20,c-16)) and written.isdisjoint(range(c,c+16)))
print('PASS: 14 stack stores, 56 distinct bytes; saved pointer and 16-byte config disjoint')
```
