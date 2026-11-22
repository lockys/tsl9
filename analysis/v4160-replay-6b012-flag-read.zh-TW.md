# `0x6b012`：寫七筆記錄後才取樣重播旗標

在 V1.31 參考映像的 `0x410` 路徑，`0x6b13c` 逐列呼叫本函式。**記錄寫入狀態與重播旗標是兩個不同值**：前者保存在 `s0`，後者由 `0x6b12e` 重新讀 `0x20002ef0`，傳給[快取寫回](v4160-replay-cache-flush.zh-TW.md) `0x44310`。寫回的回傳碼不參與本函式的返回值。

- 若輸入索引等於 `U8[0x20002fba]`，先呼叫兩次 `0x4358a` 再呼叫 `0x6afe0`；不相等則跳過。之後取索引低 16 位為 `i`。
- `0x440c2(512+6*i,16,sp+4)` 非零，或後續六 byte 檢查回傳非零，均**返回零**而不走本函式末端的七次寫入及寫回。這不是保證前面的子呼叫無副作用。
- 其餘路徑要求填 `ff` 到三段本地緩衝區：`[sp+4,sp+20)`、`[sp+20,sp+48)`、`[sp+48,sp+112)`。前六次 `0x4435c` 的 key 為 `512+6*i` 起連續六個，長度依次為 `16,28,28,16,16,4`；第一次來源 `sp+4`，後五次均為 `sp+20`。第七次的 key 是 `0x7000+i`，長度 64，來源 `sp+48`。
- 七次呼叫之間沒有依返回碼提前停止的分支。正常返回並保持保存暫存器時，函式返回七個結果按位 OR 的低 byte；傳給 `0x44310` 的卻是最後才讀的旗標。這能定位旗標的讀者，但不能排除子呼叫改寫它；沒有設備執行證據。

重現：參數為同一 V1.31 參考 BIN。檢查七個實際 JAL 目的、讀取位址與返回路徑，並核對三段緩衝區的邊界。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('6b012 evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def call(p):
    w=int.from_bytes(raw(p,4),'little'); ck(w&4095==239)
    d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    return p+(d^1048576)-1048576
ck(all(call(p)==0x4435c for p in (0x6b0ba,0x6b0c8,0x6b0d6,0x6b0e8,0x6b0fa,0x6b10c,0x6b120)))
ck(raw(0x6b124,18).hex()=='b73700201374f40f498c03c507ef1374f40f')
ck(0x20003000-272==0x20002ef0 and call(0x6b136)==0x44310)
ck(raw(0x6b13a,2).hex()=='25b7' and raw(0x6b060,4).hex()=='01442285')
ck([p+n for p,n in [(4,16),(20,28),(48,64)]]==[20,48,112])
print('PASS: seven record calls; fresh flag argument; separate saved result')
```
