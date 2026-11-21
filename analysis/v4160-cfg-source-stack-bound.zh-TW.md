# 0x400a4 配置指標：六 byte 判斷是讀，64-byte 複製方向是離開 APP 堆疊

取 v4.1.60 APP `0x19aec` 的呼叫，按前輪名義 frame，配置起點 `C=0x2000ff70`，APP 保存 s0 在 `C+72`。V1.31 參考槽 `0x400a4` 是 `0x43c7e`。在通過入口檢查的路徑，`0x43c9a` 把 C 留在 s1，供後續呼叫使用。

1. `0x43ca6` 呼叫候選 RAM 函式 `0x200004bc(C+24,255,6)`。這不是把六個 byte 填成 255：它逐 byte **讀取**，遇第一個非 255 就返回 0，六個都是 255 才返回 1。後者在 `0x43cb2` 跳到共用出口，返回狀態 3，不繼續複製。候選函式只暫時清除及恢復外設 word `0x4002420c`，不寫配置。
2. 通過後續檢查才在 `0x43cd2` 清 `D=0x200031ec` 起的 64 bytes；`0x43ce4` 呼叫候選複製函式，參數是 **`(D,C,64)`**。若兩個候選如已分析的正常語意返回且保留 s0、s1，讀取區間為 `[0x2000ff70,0x2000ffb0)`，寫入是 `[0x200031ec,0x2000322c)`。沒有向 APP 堆疊反向複製。resident 自己的三個保存 word 位於 `0x2000ff54/58/5c`，也不碰 APP 的 `0x2000ffb8`。

這排除了上述檢查、清除與複製作為破壞 APP 保存值的來源，**不是整個初始化都已排除**。後面 `0x43d38` 經配置副本 +44 呼叫，`0x43d4c` 再進 `0x43b3e`；巢狀呼叫的寫入須另算。資料來自參考 carrier，不代表裝置 ROM；不假設實際六個 byte 的值。

重現：傳入 V1.31 carrier。檢查呼叫的寄存器設定、PC-relative 目標和比較函式機碼；有限迴圈解碼三個核心指令，以全相同及每個位置的所有單 byte 差異核對第一次停止的位置。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('config source evidence mismatch')
def raw(p,n):return b[p-0x40000:p-0x40000+n]
def w(p):return int.from_bytes(raw(p,4),'little')
def target(p):
    x,y=w(p),w(p+4);ck(x&4095==151 and y&0xfffff==0x80e7);return (p+(x&0xfffff000)+((y>>20^2048)-2048))&0xfffffffe
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22');ck(w(0x400a4)==0x43c7e and [target(p) for p in (0x43ca6,0x43cd2,0x43ce4)]==[0x200004bc,0x2000039c,0x20000332]);ck(raw(0x43c94,18).hex()=='411126c21946aa849305f00f610506c622c4');ck(raw(0x43cae,8).hex()=='05478d47630fe508');ck(raw(0x43cc4,14).hex()=='373400201306000481451305c41e' and raw(0x43cda,10).hex()=='13060004a6851305c41e');ck(raw(0x4072c,62).hex()=='374702408327c720232607200f10000001c53307c50019e6374702402326f7200145828005058346f5ffe397b6fee31be5fe374702402326f72005458280')
def branch(p):
    x=w(p);ck(x&0x707f==0x1063);d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;return (x>>15&31,x>>20&31,p+(d^4096)-4096)
ck(branch(0x40756)==(13,11,0x40744) and branch(0x4075a)==(10,14,0x40750));x=w(0x40752);ck(x>>20==4095 and x&0xfffff==0x54683)
def run(data):
    r={10:0,11:255,14:6};pc=0x40750
    while pc==0x40750:
        r[10]+=1;r[13]=data[r[10]-1];pc=0x4075e
        for p in (0x40756,0x4075a):
            l,h,t=branch(p)
            if r[l]!=r[h]:pc=t;break
    return int(pc==0x4075e),r[10]
ck(run([255]*6)==(1,6))
for i in range(6):
    for v in range(255):
        row=[255]*6;row[i]=v;ck(run(row)==(0,i+1))
C=0x2000ff70;D=0x200031ec;ck(D+64==0x2000322c<C and C+64==0x2000ffb0<C+72 and [C-16-16+k for k in (4,8,12)]==[0x2000ff54,0x2000ff58,0x2000ff5c]);print('PASS: 3 call targets; 1531 six-byte cases; 64-byte copy away from APP frame')
```
