# 0x19b16 尾跳：兩個連續 frame 重用同一個 s0 保存位置

令 `E` 為 APP 函式 `0x19b16` 的入口 SP。其 `-16` frame 在 `0x19b24` 把來時的 s0 存在 `E-8`。登記、校時正常返回且保存值未變時，`0x19b3e` 從同址取回 s0。`0x19b40` 用 **s1**（不是 s0）讀 `[s1+88]` 到 t1，然後還原 ra、s1 和 SP，以 `jr t1` 尾跳，沒有改寫返回位址。若 s1 仍為 `0x40000`，V1.31 參考槽 `[0x40058]` 指向 `0x43728`；正常返回的目的地是 APP `0x8eb0`，不是 `0x19b56`。

候選排程器入口 SP 已回到 `E`。它建立 `-48` frame，`0x43734` 存 s0 到 `sp+40`，也就是 **同一個 `E-8`**。長路徑在 `0x4378e` 會把任務 ID 放入 s0，故 s0 並非全程不變。失敗返回 0 的 `0x437b2` 和成功返回 1 的 `0x4381c` 均進入 `0x437b4` 的恢復序列；`0x437b6` 從 `sp+40` 載回 s0，`0x437c6` 還原 SP，`0x437c8` 返回。ra 的兩次保存也重用同一地址 `E-4`。這是前一個 frame 結束後才重用，並非同時存在的兩份備份。

**結論：**若進入時 s0 是 `0x40000`、參考槽綁定成立、兩段執行各自正常返回、保存字保持至各自載回且 SP 正確，則回到 `0x8eb0` 時 s0 仍為 `0x40000`。不要求每個巢狀呼叫全程不碰 s0；仍不能以此證明未知回呼不改堆疊，亦不代表設備一定使用 V1.31。

核對方式：Python 參數依序為 decoded APP、V1.31 carrier。解碼兩對壓縮 stack word 存取及成功出口跳轉；框架大小和尾跳另核對機碼。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(x).read_bytes() for x in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('tail frame evidence mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def raw(p,n):
    blob,base=(b,0x40000) if p>=0x40000 else (a,0x8000);return blob[p-base:p-base+n]
def h(p):return int.from_bytes(raw(p,2),'little')
def frame(save,load,size,reg):
    s,l=h(save),h(load);ck(s&0xe003==0xc002 and l&0xe003==0x4002 and (s>>2&31)==(l>>7&31)==reg)
    u=((s>>9&15)<<2)|((s>>7&3)<<6);v=((l>>4&7)<<2)|((l>>12&1)<<5)|((l>>2&3)<<6);ck(u==v);return u-size
ck(h(0x19b16)==0x1141 and h(0x43728)==0x7179 and raw(0x19b40,4).hex()=='03a38405' and raw(0x19b52,4).hex()=='41010283' and int.from_bytes(b[88:92],'little')==0x43728)
ck(frame(0x19b24,0x19b3e,16,8)==frame(0x43734,0x437b6,48,8)==-8);ck(frame(0x19b22,0x19b44,16,1)==frame(0x43732,0x437b4,48,1)==-4)
ck(raw(0x8eac,4).hex()=='ef00b146' and h(0x4378e)==0x842a and h(0x437b2)==0x4501 and h(0x4381c)==0x4505 and raw(0x437c6,4).hex()=='45618280');x=h(0x4381e);ck(x&0xe003==0xa001);d=((x>>12&1)<<11)|((x>>11&1)<<4)|((x>>9&3)<<8)|((x>>8&1)<<10)|((x>>7&1)<<6)|((x>>6&1)<<7)|((x>>3&7)<<1)|((x>>2&1)<<5);ck(0x4381e+(d^2048)-2048==0x437b4)
print('PASS: slot 0x40058 -> 0x43728; both frames save/reload s0 at E-8 and ra at E-4; shared return sequence')
```
