# 主迴圈的回呼槽 0x200031d0：登記、清除與 a0 的首次使用

V1.31 候選 `0x43b28` 是五格 32-bit 指標表的寫入器：只有無號 `a1 <= 4` 才把 a0 寫到 `0x200031c8 + 4*a1`。前篇主迴圈讀的 `0x200031d0` 是索引 2。`0x43b6e` 的初始化呼叫以起點 `0x200031c8`、填值 0、長度 20 涵蓋全表，前提是 fill 如預期完成。

* `0x65cb8` 呼叫寫入器，a1=2，a0=`0x20003000-856=0x20002ca8`。`0x657c2` 則以同一索引和 a0=0 尾跳到寫入器，清除而非呼叫該回呼。這兩處不證先後或所有寫入來源。
* 若主迴圈確實呼叫該登記值，搬移後入口 `0x20002ca8` 的來源為 `0x42f18`。在 Xwchc 解碼下，先讀 `U8[0x20003519]` 至 a5。非零時直接在 `0x20002d4a` 返回，既沒讀也沒改 a0；因此即使傳入 6，這也不是依 6 分支。
* 若該 byte 為零，`0x20002cca` 以 `[0x200031e0]` 間接呼叫，之前不碰 a0。在已分析的 APP 時鐘綁定 `0x191c6` 下，函式先等候兩對周邊讀值各自相等，第一個碰到 a0 的指令是 `0x191f6: lhu a0,-2024(a1)`，以新樣本覆寫它；若提早一直等候則不達該點。若時鐘正常返回，`0x20002cda` 比較的是 s0 與時鐘回傳值，不是取消碼。若綁定不同，不作此推論。

上述為離線、指定路徑和成功記憶體存取下的資料流。沒有認定裝置安裝此 ROM，也未把登記寫入當作執行。重現：依序傳入 decoded APP 與 V1.31 carrier。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(ok):
    if not ok: raise ValueError('slot 2 evidence mismatch')
def raw(buf,off,h):
    v=bytes.fromhex(h);ck(buf[off:off+len(v)]==v)
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(b,0x3b28,'914763e9b700b73700208a059387871cbe9588c18280')
raw(b,0x25c92,'3735002089459356870003474103130585caa30009006207558f2324e9001147a306040058a4efd01de7')
raw(b,0x257bc,'8945014541016fe06db6')
for off,rd in [(0x25cb8,1),(0x257c2,0)]:
    x=int.from_bytes(b[off:off+4],'little');v=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    ck(x&4095==111+128*rd and 0x40000+off+(v^1048576)-1048576==0x43b28)
p=0x2b0+(0x20003000-856)-0x20000040;ck(p==0x2f18)
raw(b,p,'b737002093874751dc3393f7f70fd1ebb737002083a7071e411122c44ac006c626c2829737390020930709568047130909566302a406')
x=int.from_bytes(b[p+8:p+10],'little');d=(x>>12&1)|(x>>5&3)<<1|(x>>10&3)<<3;ck(x&0xe003==0x2000 and (x>>2&7,x>>7&7)==(7,7) and 0x20003514+d==0x20003519)
raw(b,0x270+0x2d4a,'8280')
raw(a,0x191c6-0x8000,'37360040835686810357868142074183e31ad7fe373600408356c6818357c681c207c183e39ad7feb735004003d6858103d58581')
print('PASS: indexed setter; install and clear; byte gate; clock overwrites incoming a0')
```
