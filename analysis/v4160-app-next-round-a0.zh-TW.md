# 取消碼通過空閒服務後：APP 下一輪的三個首次覆寫點

只分析原始 v4.1.60 APP。起點是假設 `0x819c` 的間接服務正常返回 `0x819e`，且 a0 仍是原先的取消碼 6；不要求裝置安裝任何指定 ROM。以下假設取指、記憶體存取、CSR 操作成功，正常堆疊與返回位址未受干擾。

| 從 `0x819e` 起的條件（依序） | 原 a0 第一次被使用的方式 |
|---|---|
| `0x17004` 讀 `gp+360`，bit 0 為 1 | `0x17012: li a0,1`，覆寫後才呼叫 `0x16b0a`。 |
| bit 0 為 0；`0x17020` **重讀**同一 byte，bit 1 為 1 | `0x1702c: li a0,2`，也不是比較 6。 |
| 兩次測得的對應 bit 都為 0；下一個函式掃到非空佇列項 | `0x12ca2: addi a0,sp,8`，以目的緩衝區指標覆寫。第一筆也可能出現在索引 31。 |
| 兩個 bit 都未設、32 次讀到的項目半字全為零 | 兩次直接呼叫均原樣返回。`0x81a6` 儲存 s0，`0x81a8` 跳回 `0x8198`；`0x819c` 仍可把 6 帶給重新載入的服務，APP 在此之前沒有讀它。 |

`0x819e`、`0x81a2` 是寫 ra 的直接 JAL，不是把服務返回值存進佇列。這裡的結論是一次 APP 迭代內的資料來源，不是裝置必然保持空閒、回呼忽略 a0 或迴圈必定終止的證明。

重現：將 decoded APP 路徑作為參數。以下固定映像身分與指令窗，解碼兩個 JAL，並對手工轉錄的分支條件列舉兩次獨立 byte 取樣及 33 種首個非空位置（含全空）；不是通用 CPU 模擬。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok:raise ValueError('APP next-round evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(pc,h):
    v=bytes.fromhex(h);ck(b[pc-0x8000:pc-0x8000+len(v)]==v)
raw(0x8198,'832709008297efe05066efa0702b80c0c5bf')
raw(0x17002,'411183c7811606c613f7170009cbf99b05452384f116eff03fafa384011683c7811613f7270009cbf59b09452384f116eff09fad23850116b24041018280')
raw(0x12c58,'5d71a6c2cac04ede52dc56da5ad85ed686c6a2c48144979aff1f938aaa3c314b13098008b7090400054a938b410533846403569483570400c207c183a9cf7330098083a7c9043146a28528008297')
raw(0x12cee,'850493070002e399f4f8b640264496440649f259625ad25a425bb25b61618280')
for pc,target in [(0x819e,0x17002),(0x81a2,0x12c58)]:
    x=int.from_bytes(b[pc-0x8000:pc-0x8000+4],'little');ck(x&4095==0xef)
    d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(pc+((d^0x100000)-0x100000)==target)
counts=[0]*4
for x in range(256):
    for y in range(256):
        for i in range(33):counts[0 if x&1 else 1 if y&2 else 2 if i<32 else 3]+=1
ck(counts==[1081344,540672,524288,16384]);print('PASS: four APP windows, two JAL targets, 2162688 modeled combinations:',counts)
```
