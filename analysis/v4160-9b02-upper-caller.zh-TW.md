# `0x9b02` 傳回的取消狀態，在 `0x14316` 的上層未被使用

原 APP 的半字對齊位置中，直接 JAL（任意 rd）及 RV32C 的 C.J / C.JAL 只有 `0x14316: jal ra,0x9b02` 符合目標。這不排除間接呼叫或其他形式的跳轉。

- **呼叫前**：`0x1430a..0x14316` 算兩值 XOR 的 bit 4。不同才呼叫，傳的是 `(a4 >> 4) & 1`，不是取消狀態。
- **正常返回後**：`0x1431a` 重新讀取 `P = word[s1]`、`byte[s0+24]` 及 `byte[P]`。`0x14328` 判斷的是兩個新讀 byte 的低三位是否相等，不是 `a0 == 6`，也不是沿用呼叫前所讀的值。
- **兩個分支都不消費 a0**：相等就跳過 `0xfa3c`；不相等才呼叫它。該 leaf 只把 `gp+276` 的 byte 複製到 `gp+277`，不讀 `a0`。匯合後 `0x14336: lw a0,0(s1)` 覆蓋取消結果。因此在此直接呼叫者，`6` 既不控制分支，也不作為下次間接呼叫的參數。這不排除先前的記憶體副作用影響重讀值。

重現：Python 3，參數為原 decoded BIN。逐位置反向編碼到指定目的的跳轉，並核對上述兩條路徑的指令。這不是硬體執行測試。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes(); base=0x8000; target=0x9b02
if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('image')
hits=[]
for i in range(0,len(b)-1,2):
    p=base+i; d=target-p; x=int.from_bytes(b[i:i+4],'little')
    j=0x6f|((d>>20&1)<<31)|((d>>1&1023)<<21)|((d>>11&1)<<20)|(d&0xff000)
    if i+4<=len(b) and -(1<<20)<=d<(1<<20) and (x&~0xf80)==j: hits.append((p,'jal',x>>7&31))
    cj=sum(((d>>k)&1)<<n for n,k in enumerate((5,1,2,3,7,6,10,8,9,4,11),2))
    if -2048<=d<2048 and (x&65535) in (0x2001|cj,0xa001|cj): hits.append((p,'compressed',None))
if hits!=[(0x14316,'jal',1)]: raise ValueError(hits)
for p,h in [(0x1430a,'b98fc18b91c7135547000589ef50cffe9c400347840183c70700b98f9d8b99c3efb02ff1370904008327c9048840'),(0xfa3c,'9387411103c70700a380e7008280')]:
    v=bytes.fromhex(h)
    if b[p-base:p-base+len(v)]!=v: raise ValueError(hex(p))
print('PASS: one direct encoding; both paths reach the a0 overwrite at 0x14336 on normal execution')
```
