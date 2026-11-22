# 從初始化寫 1 到 RF 回呼重新取樣：補上 `0x642fc` 的呼叫

不能只看三個 32-bit 跳轉。V1.31 參考 ROM 在 `0x642ea` 將狀態 `0x2000351b` 寫為 1 後，先寫兩個相鄰欄位（`0x20003538`、`0x20003534`，各四 bytes），然後 **`0x642fc` 用 16-bit `c.jal` 呼叫 `0x6430e`**，才依序進 `0x660ce`、`0x638ea`，最後尾跳 `0x641b0`。

新增核對的 `0x6430e..0x64348` 無子呼叫。它從 `[0x2000353c]` 載入基址一次，依序在偏移 `20,28,36,44,52,60,68,76,116,8,12` 各寫一個 word。`[0x20003538]` 的值只用作第九筆的資料，不是寫入指標。若基址保持父函式設的 `0x40024200`，這 11 筆不會寫入狀態 byte。

與[其他子函式的寫址清單](v4160-role-64298-three-callees.zh-TW.md)合看：在已設外設基址保持、正常返回、堆疊不與狀態重疊、無非同步寫入或外設間接副作用的條件下，這段路徑沒有把狀態從 1 改為 3。`0x641b0` 通過兩次狀態檢查與基址判斷後，到 `0x641f8` 才首次呼叫 `0x63eda`；其外設低兩位非零才重新讀狀態。在這些前提下，回呼 `0x63f26` 不會被選中。`0x6645c` 等後續子呼叫都在這次取樣之後，不能倒過來解釋它。結論限同一次同步路徑，不是裝置上狀態恆等於 1。

以下在 repo 根目錄執行，參數為 V1.31 主區。檢查完整 helper 的指令邊界：除列出的算術、兩次載入與 ret 外，只接受以 a5 為基址的 `c.sw`，並從指令解出來源與偏移。

```python
from pathlib import Path
import sys
sys.path.insert(0,'analysis')
from check_v131_role_state_gate import check
from check_v131_descriptor_edges import edges
r=Path(sys.argv[1]).read_bytes(); check(r)
def ck(x):
    if not x: raise ValueError('state interval mismatch')
for pc,t,n,kind,rd in [(0x642fc,0x6430e,2,'CJ',1),(0x642fe,0x660ce,4,'JAL',1),(0x64302,0x638ea,4,'JAL',1),(0x6430a,0x641b0,4,'JAL',0),(0x641f8,0x63eda,4,'JAL',1)]:
    ck(edges(r[pc-0x40000:pc-0x40000+n],pc,t)==[(hex(pc),kind,rd)])
def ledger(code):
    other=[]; stores=[]; i=0
    while i<len(code):
        h=int.from_bytes(code[i:i+2],'little'); n=4 if h&3==3 else 2
        ck(i+n<=len(code)); raw=code[i:i+n]; i+=n
        if n==2 and h&0xe003==0xc000:
            ck(8+(h>>7&7)==15); stores.append(((h>>10&7)*8+(h>>6&1)*4+(h>>5&1)*64,8+(h>>2&7)))
        else: other.append(raw.hex())
    ck(other=='b7370020 83a7c753 1307c008 9306c006 1306c003 37370020 03278753 4167 7d17 3d67 3d07 8280'.split())
    return stores
expected=[(20,14),(28,13),(36,14),(44,12),(52,14),(60,12),(68,14),(76,13),(116,14),(8,14),(12,14)]
code=r[0x2430e:0x2434a]; ck(ledger(code)==expected)
bad=bytearray(code); bad[0x6433a-0x6430e]^=4; ck(ledger(bad)!=expected)
print('PASS: 5 transfers; 11 decoded word stores; changed store source detected')
```
