# 空閒路徑的兩個子函式：傳入的 6 有沒有被讀？

接續 `v4160-post-slot2-a0-frontier.zh-TW.md`。以下針對 V1.31 參考程式、Xwchc、正常存取及正常返回；「原值」是進入函式時的 a0，不假設真機曾傳入 6。

|入口|原值的去向|
|---|---|
|`0x200004fa` 計時器掃描|表頭 `[0x200031e8]` 為零就返回，保留原值。首節點的事件半字為零時，先解鏈，`0x2000054e: mv a0,s0` 用節點指標覆寫。非零時 `0x20000560` 呼叫 `[0x200031e0]`，到呼叫前不讀寫 a0。只有在已分析的時鐘綁定 `0x191c6` 下才能斷言：若輪詢完成，`0x191f6` 用樣本覆寫原值；`0x20000564` 的減法讀的是服務返回值。|
|`0x63dd0` 狀態處理|讀狀態 byte 選路，不比較傳入 a0。狀態 8 路徑的首寫是 `0x63e02` 從 `[0x20003564]` 載入新值，或 `0x63e4c` 直接設零。其他路徑可原樣返回，或保留原值進入 `0x6020a`（呼叫）／`0x57dae`（尾跳）。狀態 6、7 是分次重新讀取，不能當作對同一次快照的 switch。|

兩個下游函式都可能在不碰 a0 的情況下返回；否則 `0x60262: li a0,6` 或 `0x57df6: li a0,3` 是首寫。**新載入的常數 6 與取消碼數值相同，資料來源不同**。若 `0x6020a` 原樣返回，呼叫者從 `0x63e2c` 繼續，不代表整條上層當場返回。若時鐘綁定未知，不對間接呼叫內部作結論。

重現：傳入 V1.31 carrier。對固定映像從各入口解碼直接分支，止於 a0 讀寫、呼叫、尾跳或返回，檢查所有靜態終點；不推定所有分支均可達。保留堆疊與一般暫存器之資料不在此測試內。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v:raise ValueError('first-a0 mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sx(x,n):return (x^(1<<(n-1)))-(1<<(n-1))
def walk(start,end):
    todo=[start];seen=set();out=set()
    while todo:
        p=todo.pop()
        if p in seen:continue
        ck(start<=p<end);seen.add(p);i=p-0x40000 if p<0x20000000 else p-0x20000000+0x270
        x=int.from_bytes(b[i:i+4],'little');h=x&65535;rd=x>>7&31;r=x>>15&31;s=x>>20&31;op=x&127;nr=[];nw=[];term='';n=p+4
        if h&3!=3:
            n=p+2;q=h&3;f=h>>13;u=8+(h>>7&7);v=8+(h>>2&7);z=h>>2&31
            if q==0 and f in (1,2):nr=[u];nw=[v] # vendor LBU or C.LW
            elif q==2 and f==1:nr=[u];nw=[v] # vendor LHU
            elif q==2 and f==5:nr=[u,v] # vendor SH
            elif q==2 and f==6:nr=[2,z]
            elif q==2 and f==2:nr=[2];nw=[rd]
            elif q==1 and f==0:nr=[rd];nw=[rd]
            elif q==1 and f==3:nw=[rd];nr=[2] if rd==2 else []
            elif q==1 and f==2:nw=[rd]
            elif q==1 and f==4 and h>>10&3==2:nr=[u];nw=[u]
            elif q==1 and f in (6,7):
                nr=[u];d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5;todo.append(p+sx(d,9))
            elif q==2 and f==4 and z==0:nr=[rd];term='ret' if h==0x8082 else 'indirect'
            elif q==2 and f==4 and not h&4096:nr=[z];nw=[rd]
            elif q==1 and f==5:
                d=sum((h>>k&1)<<j for k,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));n=p+sx(d,12)
            else:raise ValueError(hex(p))
        elif op==55:nw=[rd]
        elif op in (3,19):nr=[r];nw=[rd]
        elif op==35:nr=[r,s]
        elif op==99:
            nr=[r,s];d=x>>31<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;todo.append(p+sx(d,13))
        elif op==111:
            d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;term=('call:' if rd else 'tail:')+hex(p+sx(d,21))
        else:raise ValueError(hex(p))
        if 10 in nr:term='read'
        elif 10 in nw:term='overwrite'
        if term:out.add((p,term))
        else:todo.append(n)
    return out
for lo,hi,want in [(0x200004fa,0x2000061a,[(0x2000054e,'overwrite'),(0x20000560,'indirect'),(0x200005da,'ret')]),(0x63dd0,0x63e58,[(0x63e02,'overwrite'),(0x63e4c,'overwrite'),(0x63e28,'call:0x6020a'),(0x63e46,'tail:0x57dae'),(0x63e56,'ret')]),(0x6020a,0x60264,[(0x6024c,'ret'),(0x60262,'overwrite')]),(0x57dae,0x57df8,[(0x57df0,'ret'),(0x57df6,'overwrite')])]:ck(walk(lo,hi)==set(want))
print('PASS: four entries; 12 first-touch/transfer endpoints; no incoming-a0 read before these endpoints')
```
