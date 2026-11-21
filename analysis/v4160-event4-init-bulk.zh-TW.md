# 四個事件任務 ID：reset 和七筆初始化清零請求

正常同步啟動、gp 保持 `0x20004000` 時，reset 的 128-byte 複製不碰 ID；接下來的逐 word 清零**會**碰到全部四個。從 `gp+128` 起以零為起點計算，分別是 word 5 的 byte 0（+148）、6:0（+152）、9:2（+166）、58:3（+363）。這些零都在註冊前，不能當作四個任務領到相同 ID 的證據。

下表是 APP 交給 `[0x40048]` 的零填充請求，採半開區間。順序依[正常初始化呼叫鏈](v4160-event4-task-id-order.zh-TW.md)，不是按位址大小排序。

|呼叫 PC|目的起點|長度|當時四個 ID 中已寫回者|
|---|---:|---:|---|
|0x8ea6|0x2000b18c|2124|無|
|0x9094|0x2000be08|180|無；隨後才寫 +166|
|0x12526|0x2000bfd4|24|+166、+148、+152|
|0x1253a|0x2000bfec|36|同上|
|0x17606|0x2000c7a0|268|同上|
|0x8fea|gp+144|3|同上；不含 +147，更不含 +148|
|0x17058|gp+360|3|同上；結尾恰為 +363，不含該 byte|

`0x8fd8` 與 `0x8fdc` 依序呼叫 `0x12506` 與 `0x175e8`。七個目的範圍都不碰四個 ID。這是 APP 參數，不是未知 provider 的寫入軌跡；需正常返回、指定暫存器保持，且 provider 僅寫指定區間。未窮盡其他初始化、非同步或間接寫入。

以下小檢查接受 decoded BIN 路徑；由映像解碼目的與長度運算元，並對照表中結果。呼叫順序及暫存器傳遞是靜態反組譯判讀，不是由此腳本執行。

```python
import sys, hashlib
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('unexpected APP evidence')
ck(hashlib.sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(p,n=4): return int.from_bytes(b[p-0x8000:p-0x8000+n],'little')
def imm(p): return int.from_bytes(w(p).to_bytes(4,'little'),'little',signed=True)>>20
def adr(p): return (p+(w(p)&0xfffff000)+imm(p+4))&0xffffffff
def ci(p):
    h=w(p,2); v=((h>>2)&31)|((h>>7)&32); return (v^32)-32
g=adr(0x186aa); ids=[g+d for d in (148,152,166,363)]
c=g+imm(0x186c6); z=g+imm(0x186de); end=adr(0x186e2)
ck((g,c,z,end)==(0x20004000,0x20004080,0x20004080,0x2000c958))
ck(not any(g<=x<c for x in ids) and all(z<=x<end for x in ids))
ck([divmod(x-z,4) for x in ids]==[(5,0),(6,0),(9,2),(58,3)])
rows=[(adr(0x8e9c),(ci(0x8e92)<<12)+imm(0x8e96)),(adr(0x908c),imm(0x9086)),(adr(0x12512),ci(0x12522)),(adr(0x1252a),imm(0x12532)),(adr(0x175f4),imm(0x175fe)),(g+imm(0x8fe6),ci(0x8fe2)),(g+imm(0x17054),ci(0x17050))]
ck(rows==[(0x2000b18c,2124),(0x2000be08,180),(0x2000bfd4,24),(0x2000bfec,36),(0x2000c7a0,268),(g+144,3),(g+360,3)])
ck(all(w(p,2)==0x9782 for p in [0x8ea6,0x9094,0x12526,0x1253a,0x17606,0x8fea,0x17058]))
ck(not any(a<=x<a+n for a,n in rows for x in ids))
print('reset copy: 0 IDs; reset clear: 4 IDs; seven fill requests: 0/28 intersections')
```
