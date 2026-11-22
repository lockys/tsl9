# 成功配置與失敗返回：哪條路會第二次讀列數？

承接[列陣列來源](v4160-replay-row-allocation.zh-TW.md)。兩次被讀的是 **`0x200031fa`**（設定基址 `0x200031ec` + 14），不是迴圈計數 `0x20002fc1`。限 V1.31 參考映像、Xwchc 與正常控制流。

|配置路徑|返回到 `0x6b96c` 之後|
|---|---|
|n₀=0|零大小直接返回零，不呼叫失敗回呼；存零後跳過第二次讀取。|
|n₀>0，找不到區塊|到 sentinel 時可能呼叫 `[0x20003220]`，但回呼正常返回後配置器自行設 `a0=0`。即使回呼改設定，也沒有第二次取樣。|
|命中有效區塊|返回 `H+8`，存入 `0x20002fbc`，再讀 cfg+14。這條成功路徑不呼叫失敗回呼。|

成功路徑的[配置器寫入](v4160-role-allocator-metadata.zh-TW.md)只有區塊 header、統計半字 `0x200031a2..a3`、兩個堆疊保存字及外設 `0x4002420c`。名義 arena 的 header 不低於 `0x200043ac`。呼叫者在兩次取樣間清列數、清指標、存返回指標，均不碰 `0x200031fa`。因此**若兩次取樣均執行，且 heap 有效、堆疊分離、沒有外設或非同步改寫，則 n₁=n₀**。此結論不保證後續每輪重讀的列數仍不變。

重現：以下以 V1.31 參考檔為參數，解出三個配置器條件跳躍、兩個返回路徑跳躍及呼叫者的零指標分支。配置大小為 16 的倍數，故 1..3 列走小區塊游標，4..255 列走大區塊游標；不推定任一請求一定成功。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('row count contract mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def jump(buf,p,kind,reg=None):
    h=int.from_bytes(buf[p:p+2],'little'); ck(h&3==1 and h>>13==kind)
    if kind==5:
        d=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5; sign=2048
    else:
        ck(8+(h>>7&7)==reg); d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5; sign=256
    return p+(d^sign)-sign
r=b[0x270:]; ck(jump(r,0x56,6,10)==0x5a and jump(r,0x58,7,11)==0x66 and jump(r,0x98,6,14)==0x5a)
ck(r[0xa0:0xa2].hex()=='0297' and jump(r,0xa2,5)==0x5a and r[0x62:0x64].hex()=='0145' and jump(r,0x64,5)==0x104)
ck(jump(b,0x2b972,6,10)==0x2b99a and b[0x2b96c:0x2b96e].hex()=='88c0' and b[0x2b978:0x2b97c].hex()=='83c7e900')
cfg=0x200031ec+14
ck(all(not (a<=cfg<a+w) for a,w in [(0x20002fc1,1),(0x20002fbc,4),(0x200031a2,2),(0x4002420c,4)]) and cfg<0x200043ac)
ck(r[0x74:0x7c].hex()=='130740036366f702' and sum(0<16*n<=52 for n in range(256))==3 and sum(16*n>52 for n in range(256))==252)
print('PASS: 6 control edges; counts zero/small/large = 1/3/252; cfg byte disjoint')
```
