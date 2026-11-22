# 無快取頁時：配置失敗返回 10，是否代表索引未變？

不代表。限 V1.31 參考 ROM、Xwchc、非零儲存基址及正常返回。`0x444e2` 重讀 cfg+12，`0x444e8/ec` 呼叫配置器 `(頁長,78)`；`0x444f0` **先**把返回值存到 `0x200031bc`，再分支。這個四位元組目的地不包含列索引 `0x20002fba`。

|條件|結果及對索引的影響|
|---|---|
|頁長為零|配置器直接回零，不查失敗回呼；呼叫者存零並返回 10，不讀頁。|
|名義頁長 256、有效區塊配置成功|對齊大小 256，大區塊游標；無論是否分割，配置器寫 header、統計半字、堆疊及外設，不呼叫失敗回呼。返回 `H+8` 後**重新比較**已快取的頁地址；不是一律讀頁。|
|抵達 sentinel，失敗回呼為零|不呼叫外部程式，回零後同樣存零、返回 10。|
|抵達 sentinel，失敗回呼非零|呼叫 `[0x20003220]`；正常返回後配置器自行回零。呼叫者仍返回 10，但不能由此排除回呼已改索引。|

在 header 位於有效名義 arena、stack 與索引分離、沒有外設或非同步改 RAM 的條件下，前三列的**配置步驟本身**可排除為索引的寫入來源。失敗回呼[初值為零](v4160-allocator-failure-slot-origin.zh-TW.md)不是呼叫時仍為零的證據。成功後要分別套用[同頁](v4160-replay-index-cache-hit.zh-TW.md)或[異頁讀取](v4160-replay-index-page-read.zh-TW.md)的條件；不從新指標推定頁內容。未識別實機 ROM。

重現：傳入 V1.31 參考 BIN。核對呼叫和配置器控制流，以及快取指標的 store；另見[配置器寫址](v4160-role-allocator-metadata.zh-TW.md)。

```python
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('allocation evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
r=b[0x270:]; ck(r[0x56:0x66].hex()=='11c199e5b747024023a68720014545a0' and r[0x94:0xa4].hex()=='0327072269d3c207dd8d0545029765bf')
ck(b[0x44e2:0x44f8].hex()=='4a249305e00497c0fb1fe78080b52320aa0251fd51bd')
p=0x444e8; u=int.from_bytes(b[0x44e8:0x44ec],'little'); j=int.from_bytes(b[0x44ec:0x44f0],'little'); ck(p+(u&~4095)+((j>>20^2048)-2048)==0x20000040)
w=int.from_bytes(b[0x44f0:0x44f4],'little'); ck((w&127,w>>12&7,w>>15&31,w>>20&31,(w>>25)*32+(w>>7&31))==(35,2,20,10,32))
ck(0x2000319c+32==0x200031bc and 0x20002fba<min(0x200031bc,0x200031a2,0x200043ac,0x4002420c))
ck(b[0x4490:0x4498].hex()=='83274a0263925707' and b[0x438a:0x438c].hex()=='2945')
print('PASS: allocation call, result store, page comparison, sentinel callback and failure return')
```
