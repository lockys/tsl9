# Task 3：校準的四次嘗試上限不是等待逾時

接續[重新排程前的第一個呼叫](v4160-task3-pre-rearm-slot.zh-TW.md)。第二個呼叫 `0x197b8` 以參數 3 尾跳原 APP `0x1929a`。下表是**實際採樣**須滿足的條件，並非曾經發生轉換就一定看得到。地址是等待迴圈的分支指令位置。

|階段|`0x4002204c` 半字 bit 15 為 1|時鐘讀值不等於本階段基準|同一半字 bit 15 為 0|再讀到 bit 15 為 1|
|---|---|---|---|---|
|初次調整，每次嘗試|19346|19390|193a8|193b4|
|第二階段|19462|194a4|194c4|194d4|
|第三階段|1959e|195e0|19600|19610|

* 時鐘不要求增加一或單調增加，只測 32 位元值不相等。`0x191c6` 先對高半字 `0x40002818`、低半字 `0x4000281c`、再對高半字，各自讀到一對相等的值；若兩組高半字不同，再取一對相等的低半字。回傳最後採用的高、低半字組合。即使外層等待的是「改變」，內層也可能因連續兩讀總不相等而不返回。
* 初次調整的 s10 從 4 開始，每次完成上述等待後才比較量測誤差；在容許區間內可提早進第二階段，否則扣一次，扣到零同樣進第二階段。只有扣完仍非零才調整後重試。故正常返回路徑有 1 至 4 次初次調整，加上後兩階段，共通過 12 至 24 個表內等待；**這不是每個等待最多讀 24 次**。卡在任一等待都不會因 s10 倒數而離開。
* 所有等待通過、後續運算與記憶體存取成功且返回狀態保持，最後 `0x196b4` 寫校準半字，`0x196ba` 返回，APP 才繼續到 `0x199bc` 的排程呼叫。這是原 BIN 的控制流程，不證明外設會給出所需讀值或排程成功。

驗證：以下 Python 接受 decoded APP 路徑，核對映像身分，直接解出 16 個輪詢分支的比較種類與回跳目的地；不模擬外設。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('calibration loop mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def branch(pc):
    x=int.from_bytes(b[pc-0x8000:pc-0x8000+4],'little'); ck(x&127==99)
    d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    return (x>>12&7,pc+(d^4096)-4096,x>>20&31)
rows=[(0x19346,0x1933e,0x19390,0x19388,0x193a8,0x193a0,0x193b4,0x193ac),(0x19462,0x19456,0x194a4,0x194a0,0x194c4,0x194bc,0x194d4,0x194cc),(0x1959e,0x19592,0x195e0,0x195dc,0x19600,0x195f8,0x19610,0x19608)]
for row in rows:
    for i,f in enumerate((5,0,4,5)):
        pc,to=row[2*i:2*i+2]; op,dst,rs2=branch(pc); ck((op,dst)==(f,to) and (rs2!=0 if i==1 else rs2==0))
for pc,to in [(0x191d6,0x191ca),(0x191ea,0x191de),(0x191fe,0x191f2),(0x19216,0x1920a)]: ck(branch(pc)[:2]==(1,to))
ck(b[0x112e8:0x112ea].hex()=='114d' and b[0x113d6:0x113e0].hex()=='7d1d137dfd0f63050d02' and b[0x116b4:0x116bc].hex()=='231bf70261618280')
print('PASS: 12 stage waits, 4 clock pair loops, retry count and return')
```
