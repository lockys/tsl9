# 首次排程的 16 bytes 從哪一塊取得？

在[首次查找讀零](v4160-first-head-init-chain.zh-TW.md)的條件以外，還需證明小區塊未被先前配置消耗。`0x43118` 寫小游標 `0x20003194`，初值 `S=0x2000418c+544=0x200043ac`。名義設定長度 `0x7000` 走 512-byte 分區：首 header 為 `(next=0x200045ac, capacity=504, tag=0)`。大小游標是不同的 word，但兩區在同一條 header 鏈；不能只憑游標不同就判定寫入不相交。

* 首次大配置及不一致分支的 256-byte 暫存配置從大游標開始。前者最小 660 bytes，後者若執行則在第一塊之後；[釋放](v4160-second-release-table.zh-TW.md)搜尋時經過 S，但只合併暫存塊與後繼，不回寫 S。配置後的函式表位於第一塊 payload。後續登記和時鐘呼叫在[已列的正常條件](v4160-first-head-init-chain.zh-TW.md)下寫這些表、固定欄位、stack 與外設，不配置小塊。較晚由 main `0x8eb0` 開始的呼叫不能倒算進本次排程之前。
* 新請求 `16` 對齊仍為 16，不大於門檻 52，從小游標讀 S。`504−16>8`，故進入分割而非走訪下一塊：剩餘 header 在 `0x200043c4`，容量 480，後繼仍是 `0x200045ac`。S 改為 `(0x200043c4,16,0xff03)`，返回 **`0x200043b4`**。這個值是 payload，不是游標，也不是 allocator header。
* 若配置後重讀的 head 仍為零，`0x43850` **先**寫 `head=0x200043b4`，其後才填入節點全部欄位。完成時以小端讀取為 `+0:ID 3`、`+1:旗標 1`、`+2:event 0x2000`、`+4:0`、`+8:期限`、`+12:0`。所以不能由「表頭已非零」推出「資料欄位已填完」。若重讀非零則走另一分支。本結論不是實機配置記錄。

以下為有限配置模型，以 V1.31 carrier 為參數。固定初始化、分流與寫入指令；對所有容量來源 byte 及是否使用暫存塊的兩條路徑，檢查分割後的完整相鄰 header 與 payload 邊界。執行的是條件模型，不是整個 ROM。

```python
from pathlib import Path
from hashlib import sha256
from struct import pack_into,unpack_from
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('first timer block mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def window(p,s): ck(b[p:p+len(bytes.fromhex(s))]==bytes.fromhex(s))
window(0x3114,'13860522232ac718'); window(0x314c,'23a0e522e11656a223130600')
window(0x2e4,'130740036366f7023737002003254719'); window(0x31e,'7a2131ef5a21636cf704'); window(0x34c,'5aa2232016012313060010c15ea1130788fffaa26ea1ee222105'); window(0x384a,'8327871e99ef2324a71e85472326050004c52311550100a11cb123220500')
s,h,e=0x200043ac,0x200045ac,0x2000b184
for c in range(256):
    k=14+3*((c>>2)+(c&3)); size=(576+6*k+3)&~3; n=h+8+size
    for temp in (False,True):
        m=bytearray([0xa5])*(e-s); put=lambda p,q,v,t:pack_into('<IHH',m,p-s,q,v,t); get=lambda p:unpack_from('<IHH',m,p-s)
        put(s,h,h-s-8,0); put(h,e,e-h-8,0); small=bytes(m[:h-s]); put(n,e,e-n-8,0); put(h,n,size,1)
        if temp:
            f=n+264; put(f,e,e-f-8,0); put(n,f,256,78); ck(get(h)[2]==1 and get(f)[2]==0); put(n,e,256+8+get(f)[1],0)
        ck(m[:h-s]==small and get(s)==(h,504,0)); old,cap,tag=get(s); ck(tag==0 and cap-16>8); tail=s+24; ptr=s+8
        put(tail,old,cap-24,0); put(s,tail,16,0xff03); ck(get(tail)==(h,480,0) and get(h)==(n,size,1))
        ck(ptr==0x200043b4 and m[ptr-s:tail-s]==b'\xa5'*16); tick_due=c*65537
        pack_into('<I',m,ptr-s+12,0); pack_into('<I',m,ptr-s+8,tick_due); pack_into('<H',m,ptr-s+2,8192); m[ptr-s]=3; m[ptr-s+1]=1; pack_into('<I',m,ptr-s+4,0)
        ck(unpack_from('<BBHIII',m,ptr-s)==(3,1,8192,0,tick_due,0) and get(s)==(tail,16,0xff03) and get(tail)==(h,480,0))
print('PASS: 512 nominal layouts; small header retained, split 504=16+8+480; payload 0x200043b4')
```
