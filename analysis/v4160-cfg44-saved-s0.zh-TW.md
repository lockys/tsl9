# 配置 +44 取樣回呼與 APP 保存的 s0

[前段](v4160-cfg-source-stack-bound.zh-TW.md)算出 APP 配置 `C=0x2000ff70`，要保護的是 `[0x2000ffb8,0x2000ffbc)`。若 V1.31 副本 +44 仍是 APP 設定的 `0x197f0`，`0x43d38` 呼叫時 SP 為 `C-32=0x2000ff50`。這次將[原 BIN 的 13 處呼叫與寫址清單](v4160-cfg44-callback-write-set.zh-TW.md)代入這個入口 SP，而非假設不同函式的堆疊天然分離。

|寫入來源|本路徑的位址|
|---|---|
|`0x197f0` 本體的 26 處堆疊寫入|frame 基址 `0x2000fed0`；最高為保存 ra 的 `[0x2000ff4c,0x2000ff50)`。回呼保存自己的 s0 在 `0x2000ff48`，不是 APP 的保存位置。|
|`0x8520` 清除暫存區|`[0x2000fef0,0x2000ff10)`，兩輪各四個 word。|
|兩次 `0x188e2` 保存 ra|各寫同一 word `[0x2000fecc,0x2000fed0)`。|
|正常返回後 `0x43d3e`|將 a0 低半字寫至 `0x200031a4`，不是寫回 APP 配置。|

所列堆疊寫入的上界（不含）距 APP 保存 s0 起點尚有 **104 bytes**。其餘已辨識 CPU store 寫外設。即使輪詢不返回，也不會執行 `0x43d3e`。此為指定綁定、名義堆疊及既有子函式分支下的靜態結論，不涵蓋中斷、DMA、裝置 ROM 身分或下一個 `0x43b3e` 呼叫。

重現：先執行上述寫址清單的 Python 檢查，再以原 APP BIN、V1.31 carrier 為順序參數執行以下補充檢查。

```python
import hashlib, sys
from pathlib import Path
a,r=(Path(p).read_bytes() for p in sys.argv[1:])
def check(x):
    if not x: raise ValueError('cfg44 frame mismatch')
check(hashlib.sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
check(hashlib.sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
check(r[0x3d34:0x3d42].hex()=='dc5791c78297b73700202392a71a')
check(a[0x117f0:0x11800].hex()=='1971130600028145081086dea6daa2dc')
check(a[0x108e2:0x108ea].hex()=='4111b727014006c6')
E=0x2000ff70-32; F=E-128; S=0x2000ffb8
writes=[(F+i,4) for i in (*range(76,128,4),*range(4,52,4))]+[(F+52,1)]
check(len(writes)==26); writes += [(F+i,4) for i in range(32,64,4)]+[(F-16+12,4)]*2
check(min(p for p,n in writes)==0x2000fecc and max(p+n for p,n in writes)==E)
check(all(p+n<=S or S+4<=p for p,n in writes) and S-E==104)
print('PASS: 26 direct stack sites, 8 fill words, 2 nested saves; gap 104 bytes')
```
