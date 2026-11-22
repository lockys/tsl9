# 每列初始化 15 bytes，不會因自己的填值改掉下一輪的列數

範圍：V1.31 參考映像 `0x6b984` 的迴圈，採 Xwchc 與既定 RAM 程式複製映射。承接[配置成功時的列數](v4160-row-count-across-alloc.zh-TW.md)。兩個 AUIPC/JALR 組合都呼叫 `0x2000039c`；不是透過可變的函式表分派。

設 P 是有效配置的首址，n 是初始列數。`0x6bab0` 讀 P，第一次填 `P+16*i` 起的六個 byte；`0x6bac8` 重讀 P，第二次填列內偏移 6..11。依[填值函式本體](v4160-event4-fill-loop.zh-TW.md)，兩次均以 `ff` 寫入，另各有兩次對 `0x4002420c` 的 word store，沒有堆疊或其他 RAM store。`0x6bade` 第三次讀 P 後，列尾在偏移 12..13 寫零半字、偏移 14 寫零 byte。**偏移 15 保留原值**，不是補零。

可逐輪推導，不必先假設每次取得同一個 P：初始 P 在名義 arena、配置至少 `16*n` bytes。當 `i<n`，上述第一個填值的每個目的都高於指標欄位 `0x20002fbc..bf` 與列數 `0x20002fc1`；外設位址也與這兩者分離。在無非同步寫入、無外設間接改寫 RAM、存取正常的前提下，第二、三次讀到同一 P，後續寫入也分離。因此下一輪重讀到相同 n。索引從 0 每輪加一並取低 byte；即使 n=255，最後處理的是 254，下一次比較在 255 退出，不會繞回 0。這不是對其他函式或真機的全域不變性證明。

重現：以 V1.31 參考 BIN 為參數。此檢查固定兩段機碼、解出兩個呼叫目標；另以刻意非零的列資料比對有限寫入模型（不是 CPU 模擬或實機測試）。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('row fill mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x60c:0x63a].hex()=='374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7')
ck(b[0x2bab0:0x2baf4].hex()=='03250900139a440019469305f00f52959750f91fe780c08d0325090019469305f00f529519059750f91fe780608c83270900850493f4f40fd297239607002387070049bd')
for pc in (0x6bac0,0x6bad6):
    off=pc-0x40000; u,j=(int.from_bytes(b[k:k+4],'little') for k in (off,off+4))
    ck(u&4095==0x97 and j&0xfffff==0x80e7 and (pc+(u&~4095)+((j>>20^2048)-2048))&0xfffffffe==0x2000039c)
rows=0
for n in range(1,256):
    p=0x200043b4; slot=0x20002fbc; count=0x20002fc1; mm=0x4002420c
    mem={slot+j:(p>>(8*j))&255 for j in range(4)}; mem[count]=n
    def base(): return sum(mem[slot+j]<<(8*j) for j in range(4))
    i=0
    while i<mem[count]:
        ck(i<n); off=16*i
        for k in (0,6):
            d=base()+off+k; ck(d>=p and d+6<=p+16*n and mm>p+16*n)
            for j in range(6): mem[d+j]=255
        d=base()+off; mem.update({d+12:0,d+13:0,d+14:0}); i=(i+1)&255; rows+=1
    ck(i==n and mem[count]==n and base()==p)
    ck(bytes(mem.get(p+j,0xa5) for j in range(16*n))==(b'\xff'*12+b'\0'*3+b'\xa5')*n)
ck(rows==32640); print('PASS: 2 fill targets; 255 counts; 32640 rows; byte 15 preserved')
```
