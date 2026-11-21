# Task 3 重新排程之前：第一個間接呼叫不是成功判斷

原 APP `0x1999e..0x199aa` 載入 `[0x401ec]` 並間接呼叫；返回點就是直接呼叫 `0x197b8` 的指令，中間沒有測試 a0。在 V1.31 參考表，該槽指向 `0x641b0`。這把[事件分支](v4160-task3-dispatch-and-rearm.zh-TW.md)接到先前從初始化路徑辨識的[外設設定程序](v4160-role-641b0-five-calls.zh-TW.md)，但**不能沿用初始化時的狀態值**。

| V1.31 的當次讀值（Xwchc 解碼） | 正常同步流程 |
|---|---|
| `0x2000351b` 第一次或第二次讀為 4 | 直接到 `0x64286` 還原堆疊並返回；第二次讀只發生在第一次不為 4 時。 |
| 兩次皆非 4，但 `U32[0x20003504] != 0x40024300` | 同樣返回，不做下述外設設定。 |
| 兩次皆非 4 且 word 相等 | 暫存並清零 `0x4002420c`，依序呼叫 `0x63eda(13)`、`0x6645c`、`0x67198`、`0x662da`、`0x6636e`。正常完成時清除 `0x2000351b`，寫回先前暫存的外設 word，走同一返回點。 |

所以**略過設定並不會取消重新排程**。反之，深入設定時有條件回呼和外設輪詢；若其中不返回，這次 APP 呼叫便尚未抵達 `0x197b8`。即使本程序正常返回，也還需 `0x197b8` 返回、指標及保存狀態有效，APP 才會發出排程要求。這是參考版本的離線分析，不是已安裝 ROM 的身分或設備是否完成校準的證明。

重現：以 decoded APP 和 V1.31 carrier 為兩個參數執行下段 Python。核對 APP 連續呼叫指令，從參考表取入口，直接解碼三個分支與五個 JAL 的目的位址。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=map(lambda p:Path(p).read_bytes(),sys.argv[1:])
def ck(x):
    if not x: raise ValueError('slot or control-flow mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(a[0x1199e:0x119ac].hex()=='b704040083a7c41e8297eff01fe1')
def w(p): return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def target(p,j):
    x=w(p); ck((x&0x7f)==(0x6f if j else 0x63))
    if j: ck((x>>7&31)==1)
    d=((x>>31)<<20|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1) if j else ((x>>31)<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1)
    sign=1<<(20 if j else 12); return p+(d^sign)-sign
ck(w(0x401ec)==0x641b0)
ck([target(p,False) for p in (0x641cc,0x641d2,0x641e6)]==[0x64286]*3)
ck([target(p,True) for p in (0x641f8,0x64246,0x6424a,0x6424e,0x64252)]==[0x63eda,0x6645c,0x67198,0x662da,0x6636e])
ck(b[0x2427e:0x24298].hex()=='a303040023a64421f2406244d2444249b249224a924a05618280')
print('PASS: APP call pair; reference slot; 3 exits; 5 calls; common return')
```
