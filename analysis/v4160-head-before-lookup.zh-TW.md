# 首次查找前：排程器本身會不會改寫串列頭？

將「清零 → 查找」切成兩段。前段已有一個容易混淆的相鄰寫入：`0x43bfc` 寫的是表指標 `[0x200031e4,0x200031e8)`，最後一個 byte 是 `0x200031e7`，不是 head。其他[配置及寫表](v4160-second-allocation-frontier.zh-TW.md)仍須 heap、表指標與 stack 有效；不能只憑這一筆不重疊，就把零一路傳到排程入口。

後段從 V1.31 參考 `0x43728` 入口到查找呼叫 `0x43808` 為止。走通過檢查的分支，排程器直接寫入的是 9 個保存用 word（入口 SP−36 到 SP−4，每 4 bytes 一筆）與外設 `0x4002420c`。兩次 `0x6df1a` 中，除數都是 1600；只要延遲保持 192000，任一無號半字係數乘延遲再加 800，分子高 word 均不超過 2。因此都走小除數路段；在 Xwchc 解讀下該段含查表讀取，但沒有 store。**不需要假定時鐘回呼前後的兩個係數相等**才能排除除法的寫入。中間的回呼若仍是 APP `0x191c6`，其輪詢也沒有 store，但可能不返回。

所以若入口 stack 分離、指定回呼及映射保持、沒有非同步改寫或外設副作用改寫 RAM，且執行到查找，查找所見的 head 等於**排程入口的 head**，並非無條件等於初始化的零。未覆蓋插入分支或裝置行為。

重現：把下列程式另存於 `analysis/`，與 `check_v4160_clock_write_sets.py` 同目錄執行，參數為 decoded APP 與 V1.31 carrier。沿用其映像身分與 helper 無 store 檢查；下列另驗兩個 JAL、成功路段完整掃描及相鄰寫入的寬度。

```python
from check_v4160_clock_write_sets import check,scan,require
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:]); check(a,b)
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def w(p): return int.from_bytes(raw(p,4),'little')
def ck(v): require(v,'head frontier mismatch')
def store(p):
    x=w(p); ck(x&0x707f==0x2023); i=(x>>25)*32+(x>>7&31); return (x>>15&31,(i^2048)-2048)
ck(raw(0x43bf8,4).hex()=='37370020' and store(0x43bfc)==(14,484) and 0x20003000+484+4==0x200031e8)
ck(w(0x43748)==0x100f)  # fence.i, not a data store
pcs=scan(b,0x40000,0x43728,0x43748)+scan(b,0x40000,0x4374c,0x43764)+scan(b,0x40000,0x4376e,0x437ae)+scan(b,0x40000,0x437ca,0x43808)
ck(pcs==[0x4372a,0x4372c,0x43732,0x43734,0x43736,0x43738,0x4373a,0x4373c,0x4373e,0x43744]); ck(raw(0x43728,2).hex()=='7971')
offs=[]
for p in pcs[:-1]:
    h=w(p)&65535; ck(h&0xe003==0xc002); offs.append(-48+4*(h>>9&15)+64*(h>>7&3))
ck(sorted(offs)==list(range(-36,0,4)) and store(pcs[-1])==(9,524) and w(0x4372e)==0x400244b7)
for p in (0x437a6,0x437ea):
    x=w(p); ck(x&4095==0xef); d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1; ck(p+(d^0x100000)-0x100000==0x6df1a)
ck(w(0x437a0)==w(0x437d2)==0x64000613 and raw(0x437ca,2).hex()=='829b')
ck(max((k*192000+800)>>32 for k in range(65536))==2<1600<65536)
print('PASS: adjacent table ends before head; 9 stack + 1 MMIO stores; both division calls bounded for all 65536 coefficients')
```
