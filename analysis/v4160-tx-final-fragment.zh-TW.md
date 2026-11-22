# 最後一段成功：先推進游標，後清總長

在 v4.1.60 APP，通知函式返回 0 不等於 TX 描述元已清空。假設同一 bank 的總長、游標與片段長度未被其他程式改寫，相關服務正常返回：

|觀察時點|APP 對描述元的明示寫入|
|---|---|
|最後一段的通知返回成功|`0x8816..0x882c` 重新取游標與片段長度，相加後將低半字寫回游標，請求事件 1。若片段恰好用盡剩餘長度，此時游標等於總長；總長尚未清零。|
|後續事件 1 實際獲派|先取總長與游標。CCC 回傳不等於 1，或回傳 1 但剩餘量為零，兩者都跳到 `0x874e`。`0x8758` 只將總長半字寫零，然後返回，不重設游標、重試計數或片段長度。|

因此不能用「最後一段成功」或「總長已清」推出晚到的事件 2 必定停止。它依當時的重試計數決定是停止還是繼續嘗試；**繼續嘗試也不等於已複製或已送達**。這是 APP 的控制流程，不是已觀察到舊事件或實機重送。事件 1 是否獲派須另證。

重現：傳入原始 decoded APP。固定指令、解碼兩條分支與兩個半字寫入；有限算術檢查涵蓋每個可能的 16-bit 總長，各取第一、中央、末端游標（含重合邊界）。

```python
import sys, hashlib
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('final TX evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(pc): return int.from_bytes(b[pc-32768:pc-32764],'little')
def target(pc):
    x=w(pc); ck(x&127==99)
    d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    return (pc+(d^4096)-4096,x>>12&7,x>>15&31,x>>20&31)
def store(pc):
    x=w(pc); ck(x&0x707f==0x1023); return (x>>15&31,x>>20&31,(x>>25<<5)|(x>>7&31))
ck(target(0x86e4)==(0x874e,1,10,15) and target(0x86fa)==(0x874e,5,0,22))
ck(store(0x8824)==(22,15,4) and store(0x8758)==(9,0,2))
ck(b[0x816:0x82e].hex()=='83574b0003d7240085455285ba972312fb0083a70b058297')
for total in range(65536):
    for cursor in (0,total//2,total):
        after=(cursor+(total-cursor))&65535; ck(after==total and total-after==0)
print('PASS: 2 branches, 2 halfword stores, cursor/post sequence; 65536 final lengths')
```
