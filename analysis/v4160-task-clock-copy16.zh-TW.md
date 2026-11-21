# 16-byte 時鐘設定複製與保存 task ID 的條件

接續[設定成功路徑](v4160-task-clock-postcopy.zh-TW.md)。複製不是只有 16 筆 RAM 寫入。若 V1.31 的 58-byte 複製函式已映到 `0x20000332`，它先從 `0x4002420c` 讀一個 word、將該處清零、執行 `fence.i`，然後才逐 byte 讀寫，返回前把先前讀得的 word 寫回同一位址。這個順序並不保證外設沒有副作用。

以 main 入口 SP=`0x20010000`、各層正常保存 SP 計，APP 的設定來源是 `0x2000ffb0`。在本機用受限 RV32 解譯器執行參考函式原始 58 bytes，對 256 個起始 task byte 各跑一次；每次均先後觀察到 16 組 `read8(src+i), write8(0x20003234+i)`，之後恢復合成 MMIO word，正常返回。逐項比對完整 RAM、事件順序與 sp/s0/s1；task byte `0x20004184` 不變。這是合成 RAM/MMIO，不是裝置 trace。

校準回來後另走的巢狀鏈 `0x43f46 → 0x43b0a → 0x43d62`，三層 frame 的 SP 依次是 `0x2000ff90/ff80/ff60`。從 11 筆 `c.swsp` 解出的 word 起址最小 `0x2000ff64`、最大 `0x2000ffac`，全在來源設定之前，不觸及 task byte。兩次校準是其他呼叫分支，不能把它們的 frame 再疊到這條鏈上。

**判定：** 在前述參考映射、正常返回、初始 SP/GP、回呼槽與基址保持、無非同步改寫等條件下，複製與這些 frame 都不會改掉登記值。這支持首次排程重讀原登記 ID（成功情境為 3）；不是無條件指定 ID，更不是排程已成功。

以下獨立檢查僅需 V1.31 carrier：確認實際分析的函式身分與各 frame 存址，不重新執行本機的 256 次解譯。使用 `python check.py <carrier>`。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('clock copy/frame evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(sha256(b[0x5a2:0x5a2+58]).hexdigest()=='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36')
ck(int.from_bytes(b[76:80],'little')==0x20000332)
def h(p): return int.from_bytes(b[p-0x40000:p-0x40000+2],'little')
sp=0x2000ffb0; saved=[]
for p,sites in [(0x43f46,[0x43f48,0x43f54,0x43f5e]),(0x43b0a,[0x43b10]),(0x43d62,[0x43d64,0x43d6e,0x43d70,0x43d72,0x43d74,0x43d76,0x43d78])]:
    size={0x1101:32,0x1141:16}[h(p)]; sp-=size
    for site in sites:
        x=h(site); ck(x&0xe003==0xc002); off=((x>>9)&15)*4+((x>>7)&3)*64
        ck(off+4<=size); saved.append(sp+off)
ck(len(set(saved))==11 and min(saved)==0x2000ff64 and max(saved)==0x2000ffac)
ck(all(not x<=0x20004184<x+n for x,n in [(p,4) for p in saved]+[(0x20003234,16),(0x4002420c,4)]))
print('PASS: candidate copy identity, 11 decoded stack stores, task byte disjoint')
```
