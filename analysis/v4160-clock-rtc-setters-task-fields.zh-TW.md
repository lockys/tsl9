# 首次校時：兩次 RTC 設定不會直接寫任務數量或容量

要接上[首次滿表到第二次登記](v4160-second-registration-after-full.zh-TW.md)，先檢查 `19b56` 中位於四個輪詢之間的兩次呼叫。它們不是同一個 setter：`19b96 → 19248(1)` 先寫半字 `0x40002808 ← 0`、`0x4000280c ← 1`；`19ba0 → 19220(0)` 寫 `0x40002818 ← 0`、`0x4000281c ← 0`。兩者都先用 `1919c` 設 `0x40002804` 的 bit 4，尾跳 `191ae` 時再讀同一半字清 bit 4；不是把入口的舊半字整個寫回。四次 `19272` 輪詢讀的是 bit **5**，不寫 RAM。

以 `9008` 入口 SP=`0x20010000` 推算，不把已返回的 frame 累加：至 `19b56` 主體 SP=`0x2000ff90`，這才是該假設下傳給 `[40074]` 的設定來源。兩個 setter 各自再扣 32，保存 a0、ra 的 word 分別是 `0x2000ff7c`、`0x2000ff8c`，兩次重用相同位置。若改從 `8e88` 入口 SP=`0x20010000` 起算，設定來源才是 `0x2000ffb0`。因此不能將[先前複製測試](v4160-task-clock-copy16.zh-TW.md)的絕對來源位址直接套到另一個入口假設。

這些 stack 與 MMIO 寫入均不與 `[0x2000319d,0x2000319f)` 的計數／容量重疊。只證指定路徑的直接寫址，須正常返回、stack 與外設映射如假設；不證輪詢必結束、外設無間接影響，也尚不能代替後續 `197b8 → 1929a` 整個校準函式的寫址檢查。

重現：傳入 decoded APP；從指令解兩組呼叫／尾跳、半字寫入位址與 stack 保存位移。

```python
from pathlib import Path
from hashlib import sha256
import sys
a=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('RTC setter mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(p,n=4):return int.from_bytes(a[p-32768:p-32768+n],'little')
def sx(v,k):return (v^(1<<(k-1)))-(1<<(k-1))
def jump(p,rd):
    x=w(p);ck(x&4095==rd*128+111);return p+sx((x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
def sh(base,p):
    u,x=w(base),w(p);ck(u&127==55 and x&0x707f==0x1023 and u>>7&31==x>>15&31);return (u&~4095)+sx((x>>25<<5)|(x>>7&31),12)
ck([jump(p,1) for p in (0x19b96,0x19ba0,0x19226,0x1924e)]==[0x19248,0x19220,0x1919c,0x1919c] and [jump(p,0) for p in (0x19244,0x1926e)]==[0x191ae]*2)
ck((w(0x19b94,2),w(0x19b9e,2))==(0x4505,0x4501)); addrs=[sh(u,p) for u,p in [(0x19254,0x19262),(0x19254,0x19268),(0x1922c,0x19238),(0x1922c,0x1923e),(0x1919c,0x191a8),(0x191ae,0x191c0)]]
ck(addrs==[0x40002808,0x4000280c,0x40002818,0x4000281c,0x40002804,0x40002804]); sizes={0x1141:16,0x1101:32}; s=0x20010000-sum(sizes[w(p,2)] for p in (0x9008,0x9250,0x8e88,0x19b16,0x19b56));ck(s==0x2000ff90)
for start in (0x19220,0x19248):
    sp=s-sizes[w(start,2)]; slots=[]
    for p in (start+2,start+4):
        h=w(p,2); ck(h&0xe003==0xc002); slots.append(sp+4*(h>>9&15)+64*(h>>7&3))
    ck(slots==[0x2000ff8c,0x2000ff7c] and all(p>=0x2000319f for p in slots+addrs))
print('PASS: 2 setter calls; 2 shared helper targets; 6 halfword store sites; both frames disjoint from task fields')
```
