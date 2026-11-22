# 「256 bytes × 3 頁」來自兩個不同來源

APP `0x19a38` 要求清空以 `sp+16` 為首的 64 bytes。`cfg+12` 是 `sp+28..29`，之後的 [APP 寫入盤點](check_v4160_cfg12_writes.py) 顯示沒有再寫這兩個 byte。反之，`0x19a54..0x19a5a` 將 `4096-2045 = 0x0803` 以 halfword 寫到 `sp+30`。以 little-endian 拆開，`cfg+14` 頁數是 **3**；相鄰 `cfg+15` 是 **8**，不是頁數的高 byte。稍後 `0x19a6a` 的另一個 `li 3` 寫到 `sp+34`，並非此頁數的來源。

若填零及 64-byte 複製正常完成，V1.31 參考副本在 `0x200031f8` 開始的四個 byte 是 `00 00 03 08`。在 WCH 壓縮指令解讀下，`0x43cf0` 讀半字、非零略過；因此原輸入會執行 `0x43cf8`，把 **256** 寫到 `cfg+12`。緊接的 `0x43cfa` 讀的是 `cfg+14` 單一 byte；因為已是 3，跳過 `0x43d00` 的預設值 **1**。四個 byte 至此為 `00 01 03 08`。所以並非 APP 直接提供頁長 256，也不是 resident 把頁數預設成 3。

**證據終點是預設值分支 `0x43d02`，不是第一次迴圈取樣。** 比對失敗後，`0x44060` 已先讀頁長給配置器，成功後 `0x4407e` 再讀頁長給填值函式；直到 `0x4408e` 才讀迴圈頁數。不能將三次取樣合併。要證明讀到初值，還須把兩欄與後續初始化、讀頁回呼、配置及填值的寫址逐段對照。不據此推論裝置安裝了該 ROM。

重跑：先跑上述 APP 寫入盤點；下列程式參數依序是 decoded APP 與 V1.31 主段。驗證兩個設定分支的來源位元組、寬度、目的、立即值及跳址；獨立改變兩欄作對照。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(x).read_bytes() for x in sys.argv[1:])
def ck(x):
    if not x:raise ValueError('geometry source mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(a[0x11a54:0x11a5e].hex()=='856713873780231fe100');word=int.from_bytes(a[0x11a56:0x11a5a],'little',signed=True);packed=4096+(word>>20)
ck(packed.to_bytes(2,'little')==bytes((3,8)))
ck(b[0x3cf0:0x3d02].hex()=='da2701e713070010daa7f82719e30547f8a7')
def step(buf):
    pc=0x43cf0;stores=[];v=0
    while pc!=0x43d02:
        h=int.from_bytes(b[pc-0x40000:pc-0x40000+2],'little');q=h&3;f=h>>13
        if q in (0,2) and f in (1,5):
            n=2 if q==2 else 1;off=8*((h>>10)&(7 if q==2 else 3))+2*(h>>5&3)+(0 if q==2 else h>>12&1);ck(8+(h>>7&7)==15 and 8+(h>>2&7)==14)
            if f==1:v=int.from_bytes(buf[off:off+n],'little')
            else:buf[off:off+n]=v.to_bytes(n,'little');stores.append((off,n))
        elif q==1 and f==7:
            d=(h>>12&1)*256+(h>>10&3)*8+(h>>5&3)*64+(h>>3&3)*2+(h>>2&1)*32;ck(8+(h>>7&7)==14);pc+=d if v else 2;continue
        elif pc==0x43cf4:v=int.from_bytes(b[0x3cf4:0x3cf8],'little')>>20;pc+=4;continue
        elif pc==0x43cfe:v=h>>2&31
        else:raise ValueError(hex(pc))
        pc+=2
    return stores
for length in (0,1,255,256,65535):
 for count in range(256):
    buf=bytearray(16);buf[12:16]=length.to_bytes(2,'little')+bytes((count,8));s=step(buf)
    ck(buf[12:]==(length or 256).to_bytes(2,'little')+bytes((count or 1,8)) and s==([(12,2)] if not length else [])+([(14,1)] if not count else []))
print('PASS: APP packed 03 08; 1280 reference default traces; nominal 00 01 03 08')
```
