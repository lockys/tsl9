# 六輪設定後：取消請求需要輪詢返回，不需要輪詢成功

在[六輪設定](v4160-selector-six-transfers.zh-TW.md)正常結束後，`0x16d8a` 呼叫 `0x169dc(selector,0)`。它先呼叫 `0x1693e(selector,15,224,0)`，正常返回後才用 `0x81b0` 取一次起始時間 B。之後每輪重新取時間 T：

|按原指令順序判斷|結果|
|---|---|
|`(T-B) mod 2^32 > 5`|返回 1。本輪不讀周邊值。|
|差值 0..5，且讀回 byte 的高三位全為零|返回 0。讀取 helper `0x16994(selector,14)` 用 3、14、0 依序呼叫傳輸，第三次的返回值才用來比較。傳輸逾時也可能返回零，故返回 0 不等於周邊確認成功。|
|差值 0..5，高三位非零|回到 `0x16a00` 重取 T；B 不變。不能在沒有時間進展或匹配樣本的假設下保證返回。|

`0x16d8e` 沒有檢查這個 0/1：它把保存的動作與 selector 放回參數暫存器後呼叫 `0x16858`。所以兩個正常返回分支都會沿這條路徑提出取消請求；還在輪詢時則尚未提出。上述結論限 selector 1、2、保存值有效與中途呼叫正常返回；不是實機時間、傳輸成功或取消結果的證據。

重播（repo 根目錄，Python）：解碼原 APP 的兩條條件分支與直接呼叫，注入時間和 byte 樣本，檢查邊界、回繞、先超時不讀值、重試後退出。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('last poll mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(p): return int.from_bytes(b[p-32768:p-32764],'little')
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
def call(p):
    v=w(p); ck(v&4095==0xef); d=(v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1
    return p+(d^1048576)-1048576
ck([call(p) for p in (0x169f4,0x169f8,0x16a00,0x16a20,0x169ba,0x169c2,0x169c8,0x16d8a,0x16d92)]==[0x1693e,0x81b0,0x81b0,0x16994]+[0x16896]*3+[0x169dc,0x16858])
pin(0x169fc,'2a899544'); pin(0x16a04,'33052541'); pin(0x16a0c,'0545'); pin(0x16a1c,'b9454e85'); pin(0x16a24,'1375050e'); pin(0x16a2c,'0145c5b7'); pin(0x16d86,'81452285'); pin(0x16d8e,'ce852285')
def branch(p,regs):
    v=w(p); ck(v&127==99); f=v>>12&7; x,y=(regs[v>>s&31] for s in (15,20)); ck(f in (1,7)); d=(v>>31<<12)|(v>>7&1)<<11|(v>>25&63)<<5|(v>>8&15)<<1
    return p+(d^4096)-4096 if (x!=y if f==1 else x>=y) else p+4
mask=w(0x16a24)>>20
def step(base,t,read):
    if branch(0x16a08,{9:5,10:(t-base)&0xffffffff})==0x16a0c: return 1
    ck(branch(0x16a08,{9:5,10:(t-base)&0xffffffff})==0x16a1c)
    p=branch(0x16a28,{8:0,10:read()&mask}); ck(p in (0x16a00,0x16a2c)); return None if p==0x16a00 else 0
n=0
for base in (0,0xfffffffc):
    for d in (0,1,4,5,6,7,0xffffffff):
        for v in range(256):
            seen=[]; result=step(base,(base+d)&0xffffffff,lambda:seen.append(v) or v)
            ck((result,seen)==((1,[]) if d>5 else (0 if v<32 else None,[v]))); n+=1
ck([step(7,7,lambda:v) for v in (224,32,31)]==[None,None,0]); print('PASS:',n,'poll samples; ordered retry then return; 9 call targets')
```
