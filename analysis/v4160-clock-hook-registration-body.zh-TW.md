# 首次校時前：初始化本體有哪些寫址？

接續[取樣返回](v4160-clock-hook-poll-return.zh-TW.md)。對 V1.31 參考映像，從 `0x43d4c` 呼叫的 `0x43b3e` 入口線性解碼至 `0x43c4c` 返回。下表只算本體 CPU store，不把函式呼叫當作沒有副作用。堆疊採入口 SP=`0x2000ff50`，兩個 WCH 壓縮 store 採 Xwchc byte 語義。

|路徑|依序直接寫入的位置|
|---|---|
|兩條路徑共有的 8 筆|`0x200031e8、0x20003230、SP−4、0x200031e0、SP−8、SP−12、0x2000319e、0x2000322c`。倒數第二筆是 byte，其餘是 word。|
|配置成功才有的 6 筆|兩個表指標槽 `0x200031c4、0x200031e4`；兩個函式表項；計數 byte `0x2000319d`；第三個函式表項。|

`0x43bc6` **先寫配置結果**，`0x43bca` 才檢查它：失敗也會把零寫到 `0x2000322c`，但這個 word 比校準回呼槽 `0x2000321c` 高 16 bytes。成功分支的三個表項須另算：若 `0x43c08` 重讀的表基址仍是名義配置指標 `0x200045b4+576`，對全部 256 個初始索引均與回呼槽分離。不要求初始索引為零，也不由此推斷表的實際容量。

**結論：**在上述基址、保存暫存器及堆疊條件下，本體兩條路徑都不直接覆寫校準回呼槽。失敗前已有四次子呼叫；成功時另有清除、`0x4329a` 和 `0x44022` 三次。這些呼叫的傳遞寫入不能用本體的 14 個位址排除；本結論不是全程保存或裝置 ROM 身分證明。

重現：傳入參考 carrier。固定映像身分，從入口按壓縮指令長度走訪，盤點 RV32 整數 store、壓縮 store 及此處 WCH store 所用編碼，再驗證條件地址。

```python
from pathlib import Path
from hashlib import sha256
import sys
def ck(x):
    if not x: raise ValueError('registration footprint mismatch')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
p=0x3b3e; sites=[]
while p<0x3c4e:
    h=int.from_bytes(b[p:p+2],'little');q=h&3
    if (q==3 and h&127==35) or (q in (0,2) and h>>13 in (5,6,7)): sites.append(p)
    p+=4 if q==3 else 2
ck(p==0x3c4e and sites==[0x3b42,0x3b50,0x3b60,0x3b62,0x3b66,0x3b68,0x3bb4,0x3bc6,0x3bf2,0x3bfc,0x3c1a,0x3c30,0x3c3e,0x3c42]);ck(b[0x3bca:0x3bcc].hex()=='2dcd')
slot=0x2000321c;E=0x2000ff50;T=0x200045b4+576
fixed=[(0x200031e8,4),(0x20003230,4),(E-4,4),(0x200031e0,4),(E-8,4),(E-12,4),(0x2000319e,1),(0x2000322c,4),(0x200031c4,4),(0x200031e4,4),(0x2000319d,1)]
for n in range(256):
    for a,w in fixed+[(T+4*((n+j)&255),4) for j in range(3)]: ck(a+w<=slot or slot+4<=a)
print('PASS: 8 common + 6 success-only store sites; 256 nominal table indices')
```
