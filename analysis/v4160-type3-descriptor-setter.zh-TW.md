# 類型 3：描述元槽的清零、設定與兩組遮罩

在 V1.31 參考 carrier 中，`0x642a4` 清零 `[0x2000350c]`；表槽 `0x401e8` 則含 `0x640b8`。後者是 setter，不是描述元：`0x640bc` 先把呼叫者提供的 a0 (=D) 存入同一槽，再測試 D 是否為零。傳零會清槽後直接返回。表項存在不等於 v4.1.60 APP 呼叫過它。

| D 非零的路徑 | 第一次 word OR 寫回 | 第二次 word OR 寫回 |
|---|---|---|
| setter `0x640b8` | 目的指標 `[D+4]`，遮罩 `[D+20]` | 目的指標 `[D+16]`，遮罩 `[D+8]` |
| 先前的 helper `0x63eae` 起的片段 | 目的指標 `[D+4]`，遮罩 `[D+8]` | 目的指標 `[D+16]`，遮罩 `[D+20]` |

兩段取指標的欄位偏移相同，**遮罩配對相反**。各段都在第一次寫完後才讀第二組欄位；不能把兩個目的位址當作預先固定的一對。若初始化的零一直保留，helper 兩筆都跳過；若走過非空設定，目前只能限定欄位，不能把它們標成特定周邊位址。

離線搜尋：在整份 carrier 的半字對齊視窗，32-bit `sw` 使用正位移 1292 的編碼共兩處，即上述 setter 和清零點；各自前一條均為 `lui a5,0x20003`。原 APP 的對齊視窗未找到 `lw rd,488(rs1)`（488 = `0x401e8-0x40000`），亦無小端序字面值 `0x401e8`。這不排除先做地址運算、從其他表載入、resident 呼叫或其他寫槽方式，不證實際 D 或實機 ROM。

重跑：Python 3，依次提供原 APP BIN 和 V1.31 參考 carrier（不要使用 `-O`）。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
assert sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
assert sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
def words(data):
    for i in range(0,len(data)-3,2): yield i,int.from_bytes(data[i:i+4],'little')
assert [(i,w) for i,w in words(b) if w&0x707f==0x2023 and (w>>25<<5 | w>>7&31)==1292]==[(0x240bc,0x50a7a623),(0x242a4,0x5007a623)]
assert b[0x240b8:0x240bc]==b[0x242a0:0x242a4]==bytes.fromhex('b7370020')
assert int.from_bytes(b[488:492],'little')==0x640b8
assert not any(w&0x707f==0x2003 and w>>20==488 for _,w in words(a)) and (0x401e8).to_bytes(4,'little') not in a
assert b[0x240c0:0x240d8].hex()=='19c9584154491c43d58f1cc3184914451c43d58f1cc38280'
assert b[0x23eb8:0x23ecc].hex()=='d44390479842518f98c2944bdc4b9842d98f9cc2'
print('PASS: 2 matching SW sites; setter slot; both mask orders; APP narrow census')
```
