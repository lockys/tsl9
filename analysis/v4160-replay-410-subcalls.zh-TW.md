# 0x410 的三個子呼叫：常數返回、逐列讀取與失敗填值

限 V1.31 參考檔及正常返回。承接[分派入口](v4160-replay-flag-resident-caller.zh-TW.md)：`0x46466` 返回零時，下列三個呼叫之間沒有測試傳回值。

|入口|本體對記憶體的操作|未決條件|
|---|---|---|
|`0x6b13c`|直接寫入只有 3 次堆疊保存；每輪重新讀 `0x20002fc1`。索引小於該 byte 且前次結果為零才以索引呼叫 `0x6b012`，否則返回。|不能用外層無全域 store 推論內層不寫。|
|`0x445ba`|只有 `li a0,0; ret`。不寫記憶體，不呼叫其他函式。|這個子呼叫可排除。|
|`0x6b286`|除 7 次堆疊保存外，本體有一個動態半字 store。索引 i 小於重新讀取的 `0x20002fc1` 時，以 `(512+6*i,16,P+16*i)` 呼叫 `0x440c2`，P 取自 `0x20002fbc`。零返回則進下一輪。|非零返回時，兩次**各自重新讀 P**，要求 `0x2000039c` 將 6 個 `ff` 分別填到列偏移 0、6；第三次讀 P 後在列偏移 12 寫零半字。不能假定三個 P 相同。|

第三個函式離開迴圈後呼叫 `0x6af88`，再按 `0x20002fb9`、`0x20002fb8` 分別決定是否呼叫 `0x6b16e`、`0x6b1d4`，最後尾跳 `0x6b25e`。若每次取得的 P 都指向足夠大的獨立列陣列，且堆疊與陣列均不含旗標 `0x20002ef0`，上述已定位的填值和直接 store 不會改旗標；這不是所有子呼叫的寫入證明。下一個優先核對的是 `0x6b012`，以及 `0x6b928` 配置的 `16*n` bytes 是否確實提供這個 P。

重現：執行以下 Python，參數為 V1.31 主參考 BIN。核對三個呼叫、內層目標、常數返回與三次重新載入；不執行設備或快取回呼。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('reference mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,h):
    z=bytes.fromhex(h); ck(b[p-0x40000:p-0x40000+len(z)]==z)
def jal(p,t,rd=1):
    w=int.from_bytes(b[p-0x40000:p-0x40000+4],'little'); d=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    ck(w&4095==(rd<<7|111) and p+(d^1048576)-1048576==t)
for p,t in [(0x6c5be,0x6b13c),(0x6c5c2,0x445ba),(0x6c5c6,0x6b286),(0x6b164,0x6b012),(0x6b2f6,0x440c2),(0x6b2aa,0x6af88),(0x6b2b8,0x6b16e),(0x6b2c6,0x6b1d4)]: jal(p,t)
jal(0x6b2da,0x6b25e,0); raw(0x445ba,'01458280')
raw(0x6b2fc,'0325090019469305f00f26959750f91fe7804009'); raw(0x6b310,'0325090019469305f00f269519059750f91fe780e007'); raw(0x6b326,'83270900be9423960400')
ck(0x6b308+0x1ff95000+148==0x6b31e+0x1ff95000+126==0x2000039c)
print('PASS: 9 transfers; zero-return leaf; 3 pointer reloads; 2 fill targets')
```
