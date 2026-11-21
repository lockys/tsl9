# 重播頁何時要求寫回？

[產生端](v4160-replay-record-producers.zh-TW.md) `0x6b8dc` 返回後，`0x6b8e4` 從 `0x20002ef0` 載入無號 byte 作為 `0x44310` 的參數，不是傳入上一個呼叫的狀態碼。以下限 V1.31 候選、Xwchc、正常記憶體存取。

|按順序檢查|不滿足時|
|---|---|
|設定 +8 的基址非零、+60 的寫回回呼非空、傳入值恰等於 1|直接返回，不呼叫回呼、不清快取。其他非零值也不行。|
|從 `0x200031bc` 載入的快取指標 P 非零|還原堆疊後返回，不清頁地址欄位。|

通過四項時，`0x4433e` 呼叫 `cfg.write(cached_address, L>>2, P)`。第一參數讀自 `0x200031c0`，**不是**先前檢查的設定基址；L 是設定 +12 的無號半字。預設 L=256 時請求 64 個 word，並非只寫該筆 64 bytes。`0x44340` 不測回傳值，而是**重新讀取快取指標**交給 `0x20000110` 釋放；所以只有在回呼未改該欄位時，傳給釋放函式的才是原 P。兩者正常返回且 s0 保持時，依次清零快取指標與頁地址。這裡沒有依回傳碼保留快取以供重試的分支；回呼未返回時也不能說已清零。要求寫回不等於實機儲存成功。

重現：參數為 V1.31 參考 BIN。固定完整函式；從原指令解出四個條件分支，枚舉入口 byte 及三個零／非零條件，對照首個呼叫或返回邊界，不執行外部回呼。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('flush evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
x=b[0x4310:0x435c]; ck(sha256(x).hexdigest()=='ff234764266498871b46f3f4bcea032559f5f0a23821d101d6d7d1586cb33dd7')
def ins(p,n): return int.from_bytes(x[p-0x44310:p-0x44310+n],'little')
def first(flag,base,cb,ptr):
    pc=0x44310
    while pc not in (0x4433e,0x44358,0x4435a):
        h=ins(pc,2); step=4 if h&3==3 else 2
        if pc in (0x4431a,0x4431e,0x44336):
            rd,val={0x4431a:(14,base),0x4431e:(14,cb),0x44336:(12,ptr)}[pc]
            ck(h&0xe003==0xc001 and 8+(h>>7&7)==rd)
            d=(h>>12&1)<<8|(h>>5&3)<<6|(h>>2&1)<<5|(h>>10&3)<<3|(h>>3&3)<<1
            if not val: step=(d^256)-256
        elif pc==0x44322:
            w=ins(pc,4); ck(w&0x1fff07f==0xd51063)
            d=(w>>31)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
            if flag!=1: step=(d^4096)-4096
        pc+=step; ck(0x44310<=pc<0x4435c)
    return pc
for f in range(256):
    for m in range(8):
        base,cb,ptr=(m&1,m&2,m&4)
        expected=0x4435a if not(base and cb and f==1) else 0x4433e if ptr else 0x44358
        ck(first(f,base,cb,ptr)==expected)
print('PASS: 2048 flag/base/callback/cache cases; 76-byte routine pinned')
```
