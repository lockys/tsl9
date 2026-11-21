# 描述項 +4 是延後讀取的來源，不是 0x135e6 的目的地

`0x135e6` 直接執行的指令沒有用傳入的 a0 定址。它檢查 PC 相對的固定狀態；條件成立時設旗標，以 `(0x1333c,0,300,0)` 呼叫 `0x9124`，正常返回後給 1，未成立則給 0。兩個描述項建立點用此結果選 100 或 10；第二處在先前 a2 非零時跳過檢查、直接選 100。這兩個數是排程參數，不是表長度。

| 邊界 | 從 APP 機碼可見的資料流 |
|---|---|
| `0x136ac`、`0x1379c` | 呼叫 `0x9124` 時 a0 都是 `0x13f36`，a3 都取自保存描述項位址的 s0。這是在交付回呼與參數，不是直接呼叫 `0x13f36`。 |
| `0x13f36` | 若被呼叫且 a0 是非空描述項 D，依序讀 `u16[D+8]`、`u32[D+4]`、`u8[D+2]`、`u16[D]`；`0x13f4e` 將其以長度 a3、表指標 a2、標記 a1、識別值 a0 傳給 `0x13e98`。 |
| `0x13e98` | 指標與長度皆非零走 `0x13b4c`，否則直接尾跳 `0x8a56`。不是兩條路都複製 256 bytes。 |
| `0x13b64` 至 `0x13b80` | 先將表指標保存於 sp+12、長度於 sp+8，向 `[0x40070]` 請求長度個 bytes。返回零不呼叫複製；非零時保留返回值作 a0，從 sp+12 載回 **a1=表指標**，a2=長度，呼叫 `[0x4004c]`，之後將新緩衝區作為 a2 傳給 `0x8a56`。 |

所以在欄位未變、正常取回同一描述項、服務及堆疊保存符合上述條件時，複製以表為來源、以新緩衝區為目的。建立描述項時只存指標，並非當下保存 256 bytes 的快照；回呼時可能讀到更新後的表內容。這不同於設定更新路徑以表為目的。未證實回呼必定執行、目標記憶體不別名或裝置 ROM 版本。

以下 Python 片段接受 decoded BIN 路徑作第一個參數，重算兩處回呼位址、三個跳轉目標並核對關鍵讀取／參數機碼。這是指令核對，不是排程器模擬。

```python
from pathlib import Path
from hashlib import sha256
import sys
b = Path(sys.argv[1]).read_bytes()
if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP')
def w(p): return int.from_bytes(b[p-0x8000:p-0x8000+4], 'little')
def sx(v,n): return (v ^ (1<<(n-1))) - (1<<(n-1))
for p in (0x136a4,0x13794):
    a,c=w(p),w(p+4)
    if a&4095 != 0x517 or c&0xfffff != 0x50513 or p+(a&0xfffff000)+sx(c>>20,12)!=0x13f36: raise ValueError('callback')
for p,rd,target in ((0x13f4e,1,0x13e98),(0x13eac,0,0x8a56),(0x13eb0,0,0x13b4c)):
    a=w(p); d=(a>>31<<20)|((a>>12&255)<<12)|((a>>20&1)<<11)|((a>>21&1023)<<1)
    if a&4095 != rd<<7|111 or p+sx(d,21)!=target: raise ValueError('JAL')
for p,h in ((0x13f40,'8356850050418345250003550500'),(0x13b64,'32c636c482971dc5a246fc44b24536862a848297')):
    if not b.startswith(bytes.fromhex(h),p-0x8000): raise ValueError('descriptor/copy operands')
print('PASS: 2 callback addresses, 3 transfer targets, descriptor fields and copy arguments')
```
