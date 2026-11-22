# 三次回呼之間，頁數與頁長是重新取樣，不是固定常數

V1.31 參考呼叫者每輪先從 `s0+14` 讀頁數，再比較索引；若要寫頁，才從 `s0+12` 讀半字頁長。**保住 RAM 內容還不夠，也要保住下一輪載入用的 s0。** APP `0x197be` 並非始終保留 s0：進入時把它存到 `24(sp)`，隨即用 s0 保存目的頁址，返回前才從同一位置取回。五個 leaf 都不改 sp 或 s0。

以進入第一輪時 `s0=0x200031ec`、頁基址 `0x08077c00`、頁長 256、頁數 3、回呼 `0x197be` 為起點。對索引 i **只使用本輪已知的設定**：`[P]` 的 word 寫入位於名義 arena；APP 資料目的只取第 i 頁；其餘寫址是既有[固定外設與 stack store 清單](v4160-cfg60-heap-separation.zh-TW.md)。這些寫址均不碰設定的基址、頁長、頁數、回呼指標。存下 s0 後的寫入也不覆蓋其保存位置。故若本輪正常返回，下一輪既取回同一 s0，也從同一組位址讀得原值。如此逐輪推得 3 次寫頁、第 4 次頁數比較退出；沒有預先假設三輪目的址全都正確。

前提：沿用[名義 stack](v4160-cfg60-init-stack.zh-TW.md)、有效且分離的配置區、相同映射、無外設／中斷等額外寫入，及條件式 WCH 指令解碼。這不證明裝置安裝該參考 ROM、設定一定如此或等待必定結束。重跑參數依序為 decoded APP、V1.31 主段、rasm2。檢查僅涵蓋回呼期間，不含首次取樣之前的初始化。

```python
from hashlib import sha256
from pathlib import Path
import subprocess,sys
a,b=(Path(x).read_bytes() for x in sys.argv[1:3]);tool=sys.argv[3]
def ck(x):
    if not x:raise ValueError('page geometry evidence mismatch')
ck([sha256(v).hexdigest() for v in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(b[0x408e:0x4096].hex()=='7c249050634df900' and b[0x40ac:0x40c2].hex()=='4e240844585cb3872503898105093e9508c20297f9b7')
ck(a[0x117be:0x117c8].hex()=='011106ce22cc32c62a84' and a[0x117e6:0x117f0].hex()=='f2406244014505618280')
for lo,hi in [(0x19764,0x1979a),(0x18e98,0x18eb6),(0x18eb6,0x18ec4),(0x18ec4,0x18ef2),(0x18ef2,0x18f56)]:
    p=lo
    for row in subprocess.check_output([tool,'-a','riscv','-b','32','-s',hex(lo),'-D',a[lo-0x8000:hi-0x8000].hex()],text=True).splitlines():
        addr,n,h,o,*args=row.split();n=int(n);ck(int(addr,16)==p and bytes.fromhex(h)==a[p-0x8000:p-0x8000+n]);p+=n
        if o in ('bne','beqz','bnez'):ck(lo<=int(args[-1],16)<hi)
        elif o=='ret':ck(p==hi)
        elif o!='sw':ck(o in 'add addi and andi lbu li lui lw mul or ori'.split() and args[0].rstrip(',') not in ('sp','s0'))
    ck(p==hi)
C=0x200031ec;A=0x08077c00;saved=0x2000ff18;stack=[saved+4,saved,saved-12];fixed=[0x40022000+n for n in (4,16,20,36)]+[0xe000f000+n for n in (0,4,16,20)]
def separate(a,n,b,m):return a+n<=b or b+m<=a
fields=[(C+8,4),(C+12,2),(C+14,1),(C+60,4)]
for i in range(3):
    body=fixed+list(range(A+256*i,A+256*(i+1),4))
    ck(all(separate(p,4,f,w) for p in body+stack for f,w in fields))
    ck(all(separate(p,4,saved,4) for p in body+[stack[2]]))
ck(all(separate(0x200043ac,0x2000b184-0x200043ac,f,w) for f,w in fields+[(saved,4)]))
print('PASS: 5 leaf register scans; 3 page footprints preserve config fields and saved s0')
```
