# 主迴圈是否會再走到設定呼叫點？

**正常迭代的迴圈本體不會。** 原 APP 的 `0x900c` 先呼叫 `0x9250`；該初始化流程中 `0x9268` 呼叫 `0x8e88`，後者在 `0x8ea8` 呼叫[設定包裝函式](v4160-config-copy-callers.zh-TW.md)。只有前一次 `0x900c` 呼叫正常返回，呼叫者才從 `0x900e` 進入 `0x8180`。`0x900e` 保存的續行地址是 `0x9012`，並非 `0x8ea8`。

`0x8180..0x8198` 是直線前置指令。迴圈本體的 6 個指令起點如下；表內的續行假設呼叫正常返回，不代表被呼叫函式內部不再呼叫其他函式。

|PC|動作|本體內續行|
|---|---|---|
|8198|從 s2 指向的位置重新載入服務指標|819c|
|819c|間接呼叫 a5|819e|
|819e|呼叫 17002|81a2|
|81a2|呼叫 12c58|81a6|
|81a6|存 s0 到 s1 指向的位置|81a8|
|81a8|無條件短跳，不寫 ra|8198|

因此無論上述三個呼叫正常回傳什麼值，本體都不比較回傳值、不執行 ret，也不順序落到迴圈之後。不能據此排除**服務或佇列回呼內部**重新進入初始化、非正常返回或裝置重置；這不是失敗回呼欄位在運行時保持零的證明。本結論不需要假設裝置裝的是哪個 ROM。

重現：傳入 decoded APP 路徑。按原始半字解碼 CJ/JAL，核對呼叫與跳轉的目標及 link register；另鎖定直線與間接呼叫指令窗。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('main-loop control mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(pc,n):return b[pc-0x8000:pc-0x8000+n]
def edge(p):
    h=int.from_bytes(raw(p,2),'little')
    if h&3==1 and h>>13 in (1,5):
        d=(h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5
        return p+(d^2048)-2048,int(h>>13==1)
    w=int.from_bytes(raw(p,4),'little');ck(w&127==111)
    d=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1
    return p+(d^0x100000)-0x100000,w>>7&31
for p,t,r in [(0x900c,0x9250,1),(0x9268,0x8e88,1),(0x8ea8,0x199e2,1),(0x900e,0x8180,1),(0x819e,0x17002,1),(0x81a2,0x12c58,1),(0x81a8,0x8198,0)]:ck(edge(p)==(t,r))
ck(raw(0x8180,24).hex()=='411122c42d6426c24ac006c637090020b73400401304a4aa')
ck(raw(0x8198,6).hex()=='832709008297' and raw(0x81a6,2).hex()=='80c0' and raw(0x9012,8).hex()=='b240014541018280')
print('PASS: 7 transfers; 3 normal call continuations; back edge to 0x8198, not config')
```
