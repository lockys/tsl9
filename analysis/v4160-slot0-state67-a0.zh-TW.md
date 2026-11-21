# `0x200007f8`：狀態 6 不是取消碼 6

V1.31 參考服務在先前的 `0x20003240` 取樣為零時進入本段。以下是搬移後 PC、Xwchc 解讀及正常記憶體存取下的靜態資料流，不是實機觀察。令 `S=0x20003514`，表基址 `T=0x200031c8`。

* `0x20000800` 讀 `S+5`；bit 0 未設就跳到既有的槽 2 路徑 `0x2000081a`。若已設，`0x20000806` 讀 `S+7` 至 **a4**，與 **a3** 的常數 6 比較，不是比較 a0。
* 首次讀到 6：清 `S+5`，呼叫 `0x20002610`，返回後從 `[T+12]` 載入槽 3。首次不等於 6 則在 `0x200008c0` **重讀** `S+7`；第二次等於 7 才清 `S+5`、呼叫同一函式，改從 `[T+16]` 載入槽 4。其他情形回到槽 2；不能假定兩次取樣必然相同。
* `0x20002610..0x20002638` 不讀也不寫 a0。它先讀 `[0x2000353c]` 作為指標；在 `S+0` 和 `S+1` 的 bit 0 均為零且指標 `+100` 的 word 非零時回到 `0x20002620` 重試。若兩個 bit 都為零且該 word 為零，另讀 `S+5`。正常離開前再次清 `S+5`。不保證輪詢會結束。
* 因此若本段輪詢正常返回，傳入的取消碼可以原樣到達 `0x20000818: jalr a5`。槽 3/4 在此**沒有非零檢查**，不可據此認定能正常執行或其目標忽略 a0。未選 3/4 才直接走先前分析的槽 2；若 3/4 回呼返回也會繼續到槽 2。

重現：傳入 V1.31 carrier。固定三段完整 bytes，另解碼五條自訂載入、兩次 JAL 和槽位偏移；最後以獨立取樣列舉分支模型，不是實際執行紀錄。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v:raise ValueError('state67 evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def val(p,n):return int.from_bytes(b[0x270+p:0x270+p+n],'little')
for p,h in [(0x7f8,'b737002093874751d833058b19cbf8339946639be60aa3820700ef10f05f5c4482971c4491c38297'),(0x8c0,'f8339d46e39be6f4a3820700ef1050541c4899b7'),(0x2610,'b7370020b736002003a6c7539387465103c74651058b19e79833058b01e7785265fbd833a38207008280')]:
    v=bytes.fromhex(h);ck(b[0x270+p:0x270+p+len(v)]==v)
for p,k in [(0x800,5),(0x806,7),(0x8c0,7),(0x2628,1),(0x2632,5)]:
    x=val(p,2);ck(x&0xe003==0x2000 and (x>>7&7,x>>2&7)==(7,6));ck((x>>12&1)|((x>>5&3)<<1)|((x>>10&3)<<3)==k)
for p in (0x812,0x8cc):
    x=val(p,4);d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==239 and p+((d^0x100000)-0x100000)==0x2610)
for p,k in [(0x816,12),(0x8d0,16)]:
    x=val(p,2);ck(x&0xe003==0x4000 and (x>>7&7,x>>2&7)==(0,7));ck(((x>>5&1)<<6|(x>>10&7)<<3|(x>>6&1)<<2)==k)
c=[0]*5
for bit in (0,1):
    for first in range(256):
        for second in range(256):c[2 if not bit else 3 if first==6 else 4 if second==7 else 2]+=1
ck(c[2:]==[130561,256,255]);print('PASS: 3 windows; 5 Xwchc loads; 2 calls; 2 slots; modeled slot 2/3/4:',c[2:])
```
