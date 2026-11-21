# 從 APP 重載 s0 到第一次角色初始化呼叫

`0x19b06` 重載之後，APP 呼叫端不是立即查表。按正常返回的順序：

|位置|哪個值被使用？|
|---|---|
|`19b06 → 19b14 → 8eac`|`0x199e2` 從 `SP+88` 重讀 s0，回到 `0x8eac`；結尾的兩次 store 寫外設，不設定 s0。|
|`8eac → 19b16`|`19b1e` 的第一個槽讀取用 **s1**，不是剛重載的 s0。`19b24` 保存傳入的 s0，`19b30` 將 s0 暫作 `gp+388`，`19b3e` 再讀回保存值。`19b54` 是尾跳而不是直接返回；由 `[s1+88]` 選到的排程函式須正常返回，並保持或恢復 s0。|
|`8eb0 → 907a`|`907c` 保存排程函式返回時的 s0。`907e` 設 s0 為 `0x40000` 供本函式查表；**這不是修復呼叫端的基址**，因 `90a6` 隨後以保存槽覆蓋 s0。`90a8` 的 byte store 不設定 s0，然後返回 `8eb2`。|
|`8eb2 → 8eb6`|主呼叫端第一次用重載後傳下來的 s0：`lw a5,416(s0)`，再 `jalr a5`。若各段均保持原值 `0x40000`，槽為 **`0x401a0`**；V1.31 參考槽內容為 **`0x6dd16`**。位址計算、槽內容與真正執行是三件事。|

名義主 frame SP `E=0x2000ffc0`。上述三個 APP 保存位置都是 `E-8=0x2000ffb8`，但屬於**不同時間**，不是同一個持續有效的快照。最終讀到的是 `907c` 所存的值（若其後該槽不變），不由 `907e` 的常數保證。只銜接已知直接指令和條件返回；不宣稱未知回呼遵守 ABI 或裝置使用這份 ROM。參見[初始化出口](v4160-init-status-s0-reload.zh-TW.md)與[最後一次保存的寫址檢查](v4160-final-init-saved-base.zh-TW.md)。

重現：依序傳入原 APP、V1.31 carrier。從原指令解直接跳轉目標、三組保存與重載位移，以及最後 LW 的實際基底和位移。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('reload-to-role edge mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p,n=4):return int.from_bytes(a[p-0x8000:p-0x8000+n],'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
for p,t in ((0x8ea8,0x199e2),(0x8eac,0x19b16)):
    x=w(p);ck(x&4095==0xef);d=(x>>31<<20)|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1;ck(p+sx(d,21)==t)
x=w(0x8eb0,2);ck(x&0xe003==0x2001);d=sum(((x>>i)&1)<<j for i,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));ck(0x8eb0+sx(d,12)==0x907a)
for st,ld,frame in ((0x199ea,0x19b06,96),(0x19b24,0x19b3e,16),(0x907c,0x90a6,16)):
    s,l=w(st,2),w(ld,2);ck(s&0xe003==0xc002 and s>>2&31==8 and l&0xe003==0x4002 and l>>7&31==8)
    so=4*(s>>9&15)+64*(s>>7&3);lo=32*(l>>12&1)+4*(l>>4&7)+64*(l>>2&3);ck(so==lo==frame-8)
x=w(0x8eb2);ck(x&0xfffff==0x42783 and sx(x>>20,12)==416 and w(0x8eb6,2)==0x9782);slot=0x40000+416;ck(int.from_bytes(b[slot-0x40000:slot-0x40000+4],'little')==0x6dd16)
print('PASS: 3 direct call edges, 3 paired s0 slots at E-8; nominal slot 0x401a0 -> reference 0x6dd16')
```
