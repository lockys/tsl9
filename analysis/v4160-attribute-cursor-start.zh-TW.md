# 服務 handle：啟動值不等於 APP 註冊時的值

V1.31 第二次啟動搬移由 `0x6eaa4` 複製至 `0x20002e70`。游標 `0x20002eec` 位於偏移 `0x7c`，對應 `0x6eb20` 的 `01 00 ff 20`；取低半字為 **1**。這是第 32 個 word，已在參考資料內，不依賴缺失的第 35 個 word。後續清零起點 `0x20002ef8` 不含它。[搬移範圍](resident-copy-order-v131/README.md)。

**順序不能只看 APP 中 `RegisterService` 的出現次數。** 原 APP 在 `0x8fb8` 載入 `[s0+304]`、`0x8fcc` 註冊自己的四列之前，已於 `0x8eb6/8ebc/8ec2` 依序間接呼叫三個 role 初始化服務。以半字對齊掃 APP 的標準 32-bit `LW`，立即數 `0x130` 只出現在 `0x8fb8`，`0x134` 未出現；這不涵蓋計算地址或 resident 內部呼叫。

對 V1.31 主區段作相同對齊的 `JAL` 目標掃描，除 wrapper `0x4cf4a -> 0x4ce22` 外，還有兩個尾跳進 `0x4cf22`：`0x49b84` 傳入計算後的列數，`0x4cfbe` 傳入固定四列。兩者是可能改變分配順序的程式位置，**不是已在 APP 前執行的兩次註冊**。若從游標 1 開始且此前沒有改動，APP 四列為 1..4；若僅有固定四列路徑先完成一次分配且無其他改動，則為 5..8。後者是條件對照，不是觀察值。要選定其一，仍需解析 role 初始化中的間接轉移及其他游標寫入；僅配置了列不代表回呼也登記成功。

離線複核：傳入原 APP、V1.31 主 carrier 和 `0x6eaa4` 資料段，順序如下。不執行初始化。

```python
from hashlib import sha256
from pathlib import Path
from struct import unpack_from
import sys
a,r,t = [Path(p).read_bytes() for p in sys.argv[1:]]
def need(x):
    if not x: raise ValueError('cursor evidence mismatch')
need([sha256(x).hexdigest() for x in (a,r,t)] == ['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450'])
o = 0x20002eec-0x20002e70
need(0x6eaa4+o == 0x6eb20 and t[o:o+4].hex() == '0100ff20')
need(a[0xeb2:0xec4].hex() == '8327041a82978327c41a82978327041c8297')
def words(b):
    for i in range(0,len(b)-3,2): yield i,unpack_from('<I',b,i)[0]
need([(i+0x8000,w>>20) for i,w in words(a) if w&0x707f==0x2003 and w>>20 in (304,308)] == [(0x8fb8,304)])
edges=[]
for i,w in words(r):
    if w&127 != 111: continue
    j = (w>>31<<20) | (w&0xff000) | ((w>>20&1)<<11) | ((w>>21&1023)<<1)
    pc=0x40000+i; target=pc+j-((j>>20)<<21)
    if target in (0x4ce22,0x4cf22): edges.append((pc,target,w>>7&31))
need(edges == [(0x49b84,0x4cf22,0),(0x4cf4a,0x4ce22,1),(0x4cfbe,0x4cf22,0)])
need(r[0xcfb6:0xcfba].hex()=='41469145')
print('PASS: cursor seed 1; three preceding role calls; two reference registration tails')
```
