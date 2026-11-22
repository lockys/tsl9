# 儲存讀取取得區塊時，另一個回呼只在配置失敗分支

接續[兩個角色的讀取路徑](v4160-pre774-role-storage-reads.zh-TW.md)。V1.31 參考碼實際有兩種配置請求，大小都是當時 `cfg+12` 的無號半字，不是記錄長度 16 或 4：

|情形|配置呼叫|標記|配置正常返回零的處理|
|---|---|---|---|
|尚無快取緩衝|`0x4411a`|`0x4e01`|`0x44122` 先把返回值寫入快取槽，`0x44126` 跳至失敗出口|
|已有緩衝，但其頁位址與所需基址不同|`0x441ac`|`0x4e02`|返回值留在 s5，`0x441b6` 跳至相同出口；此處不把它寫入原快取槽|

兩處都是 PC-relative 呼叫 `0x20000040`。若快取位址命中，`0x4419e` 直接跳 `0x44142`，這兩次配置皆不做。在首段 RAM 程式碼按參考映像搬移成功時：請求大小為零直接失敗，不呼叫失敗回呼；非零請求掃描區塊抵達 sentinel，才讀 `[0x20003220]`。該槽非零才在 `0x200000a0` 呼叫它。以區塊大小 256 為例，參數 `(a0,a1)` 分別是 `(1,0x01004e01)`、`(1,0x01004e02)`。回呼若正常返回並保持所需狀態，配置器會重新令 a0=0；兩個呼叫者都轉往 `0x44214` 返回 10，**不再載入或執行該次儲存讀取回呼**。

失敗回呼用 config+52，不是讀取回呼的 +56；[APP 的設定來源](v4160-allocator-failure-slot-origin.zh-TW.md)在指定清零、複製前提下給 +52 初值零，但這不是抵達 sentinel 時的即時值。不能斷言裝置一定會配置、一定成功，或排除非同步／後續寫入。

複核：在 repo 根目錄傳入 V1.31 主區檔。核對兩個呼叫的目標、現場形成的標記及返回分支；使用搬移映射核對回呼參數與返回零的指令。

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
r=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('storage allocation mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,tag,post in [(0x4411a,0x4e01,'08d02a867dc5'),(0x441ac,0x4e02,'aa8a39cd')]:
    i=p-0x40000; ck(edges(r[i:i+8],p,0x20000040)==[(hex(p),'AUIPC/JALR',1)])
    ck(r[i-10:i-4].hex()=='03d5c9009565'); w=int.from_bytes(r[i-4:i],'little',signed=True)
    ck(w&0xfffff==0x58593 and 0x5000+(w>>20)==tag and r[i+8:i+8+len(post)//2].hex()==post)
    ck((256<<16|tag)==(0x1004e01 if p==0x4411a else 0x1004e02))
for p,h in [(0x4419c,'5850e382e7fa'),(0x44214,'29458dbf'),(0x20000056,'11c199e5'),(0x2000005a,'b747024023a68720014545a0'),(0x20000090,'373700200327072269d3c207dd8d0545029765bf')]:
    i=p-0x40000 if p<0x20000000 else 0x2b0+p-0x20000040
    ck(r[i:i+len(h)//2].hex()==h)
print('PASS: both allocation targets, tags, null-result paths and conditional failure callback')
```
