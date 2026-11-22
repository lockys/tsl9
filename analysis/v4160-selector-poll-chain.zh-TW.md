# 兩次輪詢夾住 42 次固定傳輸：逾時返回不阻止取消

承接[末次輪詢](v4160-selector-last-poll.zh-TW.md)。針對 selector 1、2 且動作 0，從 `0x16d12`（兩個記憶體服務正常返回之後）開始。呼叫者依序要求：

1. `0x169dc(selector,128)`：時間差未超過 5 時，須 `byte & 0xe0 == 0x80` 才返回 0；時間差超過 5 則返回 1。**傳輸逾時給的零在這裡不匹配**，不同於末次輪詢。
2. 兩次 `0x16a30` 各呼叫傳輸函式三次，傳入 `2,96,32` 及 `2,112,32`。隨後[六輪設定](v4160-selector-six-transfers.zh-TW.md)再呼叫 36 次。這一段合計 42 次，沒有哪個傳輸返回 byte 被用來提早退出。
3. `0x169dc(selector,0)`：這次零可以匹配。兩次輪詢只要都正常返回，無論各自返回 0 或 1，呼叫者均到達 `0x16858(selector,0)`；沒有用返回碼當作取消的門檻。若任一次持續讀到不匹配值且時間差一直不超過 5，則可能停在該處。第一次停住時 42 次都還沒開始，第二次停住時已完成這 42 次呼叫。

若兩個輪詢都返回，令 R 為其中實際呼叫 `0x16994` 的總次數（超時且不讀值的那一輪不算）。每個輪詢先透過 `0x1693e` 呼叫四次傳輸，每次讀值另需三次，因此到取消 helper 之前合計 `50+3*R` 次 `0x16896` 呼叫。這是正常返回路徑上的呼叫數，非成功傳輸數；未假設實機時鐘一定前進。

離線檢查：核對 APP 直接呼叫、迴圈和參數指令，檢查兩個門檻對所有 byte 的差異。使用合成時鐘／傳輸序列比對返回狀態，不是整機模擬。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('poll chain mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def u(p): return int.from_bytes(b[p-32768:p-32764],'little')
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
def call(p):
    v=u(p); ck(v&4095==239); d=(v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1
    return p+(d^1048576)-1048576
pcs=(0x16d18,0x16d26,0x16d3a,0x16d7e,0x16d8a,0x16d92); ck(list(map(call,pcs))==[0x169dc,0x16a30,0x16a30,0x168de,0x169dc,0x16858])
for p in (0x16a58,0x16a60,0x16a68,0x16968,0x16970,0x16978,0x16980,0x169ba,0x169c2,0x169c8): ck(call(p)==0x16896)
pin(0x16d12,'930500082285'); pin(0x16d1c,'13060002930500062285'); pin(0x16d2a,'13060002930500072285'); pin(0x16d82,'e31569fd81452285'); pin(0x16d8e,'ce852285'); pin(0x16a52,'094532c62ec4'); pin(0x16a5c,'a2452e85'); pin(0x16a64,'32463285')
mask=u(0x16a24)>>20; first=u(0x16d12)>>20
for v in range(256): ck(((v&mask)==first)==(128<=v<=159) and ((v&mask)==0)==(v<=31))
def poll(want,samples):
    n=0
    for diff,v in samples:
        if diff>5: return 1,n
        n+=1
        if v&mask==want: return 0,n
    return None,n
for want in (first,0):
    ck(poll(want,[(5,want^128)]*4)==(None,4))
for a in (0,1):
    for z in (0,1):
        x,r=poll(first,[(2,0),(6 if a else 5,128)]); y,s=poll(0,[(3,128),(6 if z else 5,0)])
        ck((x,y)==(a,z) and 50+3*(r+s)==62-3*(a+z))
print('PASS: 16 direct calls; 256 paired byte decisions; 4 normal status pairs and 2 unfinished prefixes')
```
