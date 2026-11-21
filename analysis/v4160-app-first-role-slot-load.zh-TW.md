# APP 首次角色呼叫：檢查 0x40190 的直接載入

以 v4.1.60 decoded APP 的 `0x8e88` 為起點，`0x8e8c` 設 `s0=0x40000`。主線先在 `0x8ea6` 呼叫 `[s0+72]`，接著依序呼叫 `0x199e2`、`0x19b16`、`0x907a`；它們正常返回後，`0x8eb2` 用 **416** 而不是 **400** 作為 `lw a5,offset(s0)` 的位移，`0x8eb6` 才呼叫 a5。因此若基址仍為 `0x40000`，這一步取的是 `[0x401a0]`。V1.31 參考表中其值為 `0x6dd16`，而 `[0x40190]` 為 `0x6dc36`。

最後一個子函式 `0x907a` 自行保存 s0 並設基址 `0x40000`，先經 `+72` 請求清 180 bytes，再經 `+128` 傳入函式位址 `0x901a` 登記。它把結果的低 byte 存到 `gp+166`，並非執行被登記的函式。`0x199e2`、`0x19b16`、`0x907a` 的 s0 保存與載回槽分別為 `sp+88`、`sp+8`、`sp+8`。`0x19b16` 還原後還要尾跳；故不能只以保存指令推論所有外部呼叫都保留 s0。

**範圍與限制：**整份 APP 的 38,399 個半字對齊四 byte 視窗中，沒有標準 `lw rd,400(rs1)` 編碼，也沒有 `0x40190` 或 `0x6dc36` 的完整小端 word。這排除一種常見的直接引用形式，不排除換基址、計算位址、從 RAM 取指標或間接回呼。這不是整個初始化呼叫樹的可達性證明，亦未確認設備使用該版 resident。

重現：以 APP 和 V1.31 carrier 依序為參數；固定兩份檔案身分後核對主線、最後子函式、表值及掃描範圍。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('APP role slot evidence mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def raw(p,h):
    d=bytes.fromhex(h);ck(a[p-0x8000:p-0x8000+len(d)]==d)
raw(0x8e88,'011122cc370404003c44056606ce1306c6848145172500201305052f26ca8297ef00b133ef00b146e9228327041a8297');raw(0x907a,'411122c4370404003c4406c61306400b8145173500201305c5d782978327040817050000130505f88297b24022442383a10a41018280')
for p,h in [(0x199ea,'a2cc'),(0x19b06,'6644'),(0x19b24,'22c4'),(0x19b3e,'2244'),(0x19b54,'0283')]:raw(p,h)
ck([int.from_bytes(b[i:i+4],'little') for i in (72,128,400,416)]==[0x2000039c,0x43c4e,0x6dc36,0x6dd16]);windows=range(0,len(a)-3,2);ck(len(windows)==38399)
for i in windows:
    x=int.from_bytes(a[i:i+4],'little');ck(x&0xfff0707f!=0x19002003 and x not in (0x40190,0x6dc36))
print('PASS: APP main and final helper; 4 candidate slots; 38399 windows, 0 specified direct forms')
```
