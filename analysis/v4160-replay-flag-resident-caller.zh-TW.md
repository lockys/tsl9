# 參考 resident 的直接呼叫用的是 0x410，不是 0x418

對照[APP 九處固定偏移呼叫](v4160-replay-flag-app-parameters.zh-TW.md)，改從 V1.31 分派入口 `0x6c3d6` 反查。以每個半字為起點檢查 JAL、C.J/C.JAL 以及相鄰 AUIPC/JALR；主參考區只命中 `0x6cb68` 的 JAL-ra，條件搬移後的 RAM 程式區與 v4.1.60 APP 均未命中。搜尋完整小端目標 word，只在主參考區 `0x40168` 出現一次。這不含一般寄存器間接呼叫、非相鄰地址建構或缺失的 resident 區域。

`0x6cb3a` 讀的是相鄰設定 `0x20002ef2`，不是寫回旗標 `0x20002ef0`。循所列分支，值為 3 時進入 `0x6cb60`，隨後連續設定 `(a0,a1,a2)=(0x410,0,0)` 再呼叫；值為 2 時跳過該呼叫。`0x410` 經跳表索引 16 到 `0x6c5b4`：長度零時呼叫 `0x46466`。若返回非零，直接寫 1 到 **`0x20002fc0`**；若返回零，依次呼叫 `0x6b13c`、`0x445ba`、`0x6b286`。因此不能把非零分支的 store 算作寫回旗標 setter，也不能把尚未檢查的子呼叫視為無副作用。

重現（repo 根目錄；只讀，不接設備）：

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
r=next(Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023').glob('*00040000*bin')).read_bytes()
a=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('reference mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' and sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for base,b in [(0x40000,r),(0x20000000,r[0x270:0x2b0+2957*4]),(0x8000,a)]:
    ck(edges(b,base,0x6c3d6)==([('0x6cb68','JAL',1)] if base==0x40000 else []))
    ck([base+i for i in range(len(b)-3) if b[i:i+4]==bytes.fromhex('d6c30600')]==([0x40168] if base==0x40000 else []))
def raw(pc,h):
    z=bytes.fromhex(h); ck(r[pc-0x40000:pc-0x40000+len(z)]==z)
raw(0x6cb36,'b737002083c727ef09476386e7020d47638de700'); raw(0x6cb60,'0146814513050041eff0ff86')
raw(0x6e74c+16*4,'b4c50600'); raw(0x6c5b4,'e39f05e4ef90fdea01e9efe0ffb7ef709dffefe01fccb1bdb737002005472380e7fc81bd')
print('PASS: 1/0/0 direct encodings; selector 0x410; nonzero arm stores to 0x20002fc0')
```
