# 重送後，下一次掃描是否會選回同一個任務？

V1.31 參考 resident，位址按搬移後執行位置解讀。承接 `check_v131_retry_pending_merge.py` 的成功重送分支。`0x2000092a` 重新讀游標：零就跳過加一；非零才寫回加一的低 8 位。`0x2000093c` 有可選間接呼叫，所以 `0x20000942` 和 `0x20000946` **重新讀取**游標與任務數。游標小於任務數便返回，沒有在此直接派送；否則到 `0x2000084c` 清零並走後續服務，不是在同一次掃描內繞回表頭。

假設任務數固定、游標和表未受其他寫入、只有原任務仍有事件、後續每次都能重入掃描：ID 0 下次掃描便選回；非零末項先重設為 0，下次從表頭也會選回；非零中間項則先掃完空的後半段，**再下一次**才從表頭選回。若表頭任務持續有事件，游標可反覆停在 0；不能由重送成功推定固定延遲或公平性。不是實機或實際 resident 身分證明。

重現：將以下 Python 程式以 V1.31 carrier 路徑為唯一參數執行。固定原始指令窗，按 Xwchc 載入語義投影；只模擬有效索引與無干擾的再次掃描。

```python
from hashlib import sha256
from pathlib import Path
import sys
b = Path(sys.argv[1]).read_bytes()
def check(x):
    if not x: raise ValueError('scan evidence mismatch')
check(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p, h in [(0x836,'8347c41993961700ba969622c9ca8347c41963eec708230e0418'),(0x8d4,'850793f7f70f230ef418e3ecc7f48db7'),(0x92a,'8347c41981c78507230ef4188327891c81c782972324091c0347c41983471a00e371f7f0')]:
    v = bytes.fromhex(h); check(b[0x270+p:0x270+p+len(v)] == v)
def after(i,n):
    j = (i+1)&255 if i else 0
    return j if j<n else 0

def scan(j,n,pending):
    while j<n:
        if j in pending: return j,after(j,n)
        j += 1
    return None,0
one = two = 0
for n in range(1,256):
    for i in range(n):
        picked,j = scan(after(i,n),n,{i})
        if i==0 or i==n-1:
            check(picked==i); one+=1
        else:
            check(picked is None and j==0 and scan(j,n,{i})[0]==i); two+=1
j=0
for _ in range(32):
    picked,j=scan(j,2,{0,1}); check(picked==0 and j==0)
check((one,two)==(509,32131))
print('PASS: 509 next-scan hits; 32131 hits after one empty suffix; 32 repeated slot-zero controls')
```
