# 配置失敗回呼 cfg+52：固定地址寫入盤點

問題是[初始化給零](v4160-allocator-failure-slot-origin.zh-TW.md)之後，是否另有直接設定這四個 bytes 的程式。以下只查可以由相鄰指令直接解出有效地址的形式：LUI 或 AUIPC、可選一次同暫存器 ADDI，再接 SB/SH/SW、C.SW 或候選 Xwchc 的壓縮 byte/halfword store。以**寫入區間相交**而非起始地址相等判定。這是半字對齊編碼掃描，不是時間或可達性分析。

結果：APP 76800 bytes、參考 ROM 191078 bytes、參考 RAM 映射 11892 bytes，三者均零筆。已知的清零迴圈與設定結構複製並不屬於這類直接寫入；所以零命中不能證明呼叫當時仍為零。下一步應查設定結構整塊複製的其他呼叫者及來源，而非擴大掃描後直接斷言沒有 writer。

重現：傳入原 APP、V1.31 參考 ROM。第三區段是參考啟動複製的 RAM 映射，與 ROM 資料有重疊，不能把兩者當獨立證據。

```python
import hashlib,sys
from pathlib import Path
def ck(v):
    if not v: raise ValueError('cfg+52 census mismatch')
def sx(i): return (i^2048)-2048
def scan(b,base,slot):
    hits=[]
    def word(p): return int.from_bytes(b[p:p+4],'little')
    for i in range(0,len(b)-5,2):
        u=word(i); reg=u>>7&31
        if u&127 not in (23,55) or not reg: continue
        addr=(u&~4095)+(base+i if u&127==23 else 0); p=i+4; w=word(p)
        if w&0xfffff==(reg<<15|reg<<7|19) and p+4<=len(b):
            addr+=sx(w>>20); p+=4; w=word(p)
        if p+2>len(b): continue
        h=w&65535; q=h&3; f=h>>13
        if w&127==35 and p+4<=len(b) and w>>15&31==reg and (w>>12&7)<3:
            z=1<<(w>>12&7); d=sx((w>>25)*32+(w>>7&31))
        elif 8+(h>>7&7)==reg and (f,q) in ((6,0),(5,0),(5,2)):
            if f==6: z,d=4,8*(h>>10&7)+4*(h>>6&1)+64*(h>>5&1)
            elif q==0: z,d=1,8*(h>>10&3)+2*(h>>5&3)+(h>>12&1)
            else: z,d=2,8*(h>>10&7)+2*(h>>5&3)
        else: continue
        start=(addr+d)&0xffffffff
        if any(slot<=(start+k)&0xffffffff<slot+4 for k in range(z)): hits.append((hex(base+p),hex(start),z))
    return hits
slot=0x20003220
a,b=(Path(s).read_bytes() for s in sys.argv[1:]); ck([hashlib.sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
# Real LUI/LW from the allocator is not a writer. Change only the memory instruction for positive controls.
u=b[0x300:0x304]; ck(u.hex()=='37370020' and not scan(b[0x300:0x308],0,slot))
for d,z,hit in [(543,1,False),(543,2,True),(544,4,True),(547,1,True),(548,4,False)]:
    w=(d>>5)<<25|14<<15|{1:0,2:1,4:2}[z]<<12|(d&31)<<7|35
    ck(bool(scan(u+w.to_bytes(4,'little'),0,slot))==hit)
for label,base,data in [('APP',0x8000,a),('ROM',0x40000,b),('RAM',0x20000000,b[0x270:0x2b0+2957*4])]:
    hits=scan(data,base,slot); print(label,len(data),hits); ck(not hits)
```
