# 首次校時前：相同三個設定欄位，在複製前後有不同的退出效果

V1.31 參考程式先檢查 APP 傳入的結構，稍後才檢查 resident 的副本。兩次都看 `+8/+56/+60`（頁址、讀回呼、寫回呼），但不能共用一個「缺欄位」分支。下表假定前置檢查已過、三欄複製後未變，且通往第二個檢查的配置成功、各子呼叫正常返回。0/1 表示零／非零，不是實際指標。

|欄位組合|複製前 `0x43cb6`|複製後 `0x44022`|對首次校時的意義|
|---|---|---|---|
|頁址 0，另兩欄任意（4 組）|略過回呼檢查，進入清零及複製|返回 1，不讀頁|內層的 1 不是 APP 初始化狀態；不能據它排除之後讀 cfg+48。|
|頁址非零，任一回呼為零（3 組）|返回 6，不執行這次清零或複製|不到達|APP 進入 `0x19af0` 自跳；這次呼叫既未安裝 `cfg+48`，也不會經正常續行讀它。|
|三者皆非零（1 組）|進入清零及複製|呼叫讀回呼|這是[已恢復的 APP 初值](v4160-cfg-read-gate-44022.zh-TW.md)；是否保存 `cfg+48` 仍須計入讀回呼及後續分支。|

依據：早期的 `lw` 以 s1 為基址；晚期的三個 `lw` 從 resident 設定載入。`0x43c06` 在 `0x44022` 返回後開始取計數及表指標，並不測試 a0；`0x43d4e` 在內層正常返回後另設外層狀態零。若兩次取樣間欄位改變，早期通過的 5 種輸入各可配 8 種合成晚期狀態；只有 5/40 配對走到讀回呼。這是區分兩次取樣的檢查，不是發生機率，也不證實有寫入者或已安裝此 ROM。

重跑：傳入 V1.31 carrier。解碼兩處的 C.LW、C.BEQZ/BNEZ（含基址、目的暫存器及跳址），從實際分支選出口；固定兩個狀態值及返回後首段指令。僅測欄位檢查，不執行配置器或回呼。

```python
from pathlib import Path
from hashlib import sha256
from itertools import product
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('config gate mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def h(p):return int.from_bytes(b[p-0x40000:p-0x40000+2],'little')
def gate(load,branch,base,off,v):
    w=h(load);z=h(branch);r=8+(w>>2&7);ck(w&0xe003==0x4000 and 8+(w>>7&7)==base and ((w>>10&7)*8+(w>>5&1)*64+(w>>6&1)*4)==off)
    ck(z&3==1 and z>>13 in (6,7) and 8+(z>>7&7)==r);d=(z>>12&1)*256+(z>>10&3)*8+(z>>5&3)*64+(z>>3&3)*2+(z>>2&1)*32
    return branch+((d^256)-256) if bool(v)==(z>>13==7) else branch+2
slots=[(0x43cb6,0x43cb8,9,8),(0x43cba,0x43cbe,9,56),(0x43cc0,0x43cc2,9,60),(0x4402e,0x44036,15,8),(0x4404a,0x4404c,8,56),(0x4404e,0x44050,8,60)]
ck(h(0x43cbc)==0x4799 and h(0x44038)==0x4505 and h(0x43d4e)==0x4781 and b[0x3c06:0x3c0c].hex()=='1c3083a6441c')
def trace(start,vs):
    pc=slots[start][0];i=start
    while i<start+3 and pc==slots[i][0]:
        pc=gate(*slots[i],vs[i-start]);i+=1
        if pc==0x44046:pc=0x4404a  # addi s0,s0,492 before the load
    return pc
ck(b[0x4046:0x404a].hex()=='1304c41e');cases=list(product((0,1),repeat=3));valid=hits=stable=0
for x in cases:
    early=trace(0,x);ck(early==(0x43cc4 if not x[0] or all(x) else 0x43d50))
    if early==0x43cc4:
        for y in cases:
            late=trace(3,y);ck(late==(0x44052 if all(y) else 0x44038));valid+=1;hits+=late==0x44052;stable+=x==y and late==0x44052
ck((valid,hits,stable)==(40,5,1));print('PASS: 3 early rejects; stable 4 skips/1 read; independent snapshots 5 reads/40')
```
