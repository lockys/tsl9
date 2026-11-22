# 首次校時前：讀回不等時，配置成功與失敗要分開看

接續[讀回比較](v4160-clock-hook-read-through-return.zh-TW.md)。在 V1.31 參考程式 `0x44060`，配置呼叫使用設定 +12 的半字長度及標記 78。兩條路徑都先在 `0x44076` 寫配置結果到 `0x200031bc`，才測試它是否為零。

* **返回零：**本體只寫上述一個 word，返回 1。沒有填值、寫頁回呼、釋放，亦不清相鄰的 `0x200031c0`。這是配置器**已經返回**之後的結論，不排除它在失敗前呼叫其他函式。
* **返回非零：**若長度維持 256、區塊數為 3，每次重讀都得到原指標 P，則填入 256 個 `0xff`。三輪各把本頁地址寫在 **同一個 `[P]`**，再以 `(頁地址,64,P)` 呼叫 cfg+60，64 是 word 數。釋放接收 P；正常返回後，呼叫端依序清 `0x200031bc` 和 `0x200031c0` 並返回 0。

**對校準回呼槽 `0x2000321c..0x2000321f` 的判定：**兩條路徑的固定寫址都不重疊；成功路徑若 P 是有效 arena 物件，填值和三次 `[P]` 寫入也不重疊。[APP 寫頁回呼](v4160-mismatch-saved-s0.zh-TW.md)的名義頁範圍是 `[0x08077c00,0x08077f00)`；依[釋放寫址](v4160-44098-release-write-set.zh-TW.md)，有效 arena header、固定計帳欄位及外設暫存也與槽分離。依賴名義堆疊、Xwchc、已核對的回呼綁定、有效串列、無干擾及正常返回；未知配置失敗回呼的作用不能由任何返回碼排除。未連設備。

重現：傳入 V1.31 carrier。檢查以原始指令窗鎖定兩個出口及呼叫者寫入，並在有限模型中枚舉成功配置位置。這是呼叫邊界和位址驗算，不執行配置器或回呼。

```python
from pathlib import Path
from hashlib import sha256
import sys
def ck(x):
    if not x: raise ValueError('mismatch paths')
b=Path(sys.argv[1]).read_bytes();ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for off,h in [(0x4038,'0545'),(0x4060,'4a249305e004'),(0x4072,'1387c41908d39384c41955dd'),(0x407e,'52249305f00f0149'),(0x408e,'7c249050634df9003285'),(0x40a0,'014523a0040223a2040241bf'),(0x40ac,'4e240844585cb3872503898105093e9508c20297f9b7')]:ck(b[off:off+len(h)//2].hex()==h)
slot=0x2000321c;cache=0x200031bc;A=0x08077c00
def separate(p,n):return 0<=p<=p+n<=2**32 and (p+n<=slot or slot+4<=p)
def project(P):
    stores=[(cache,4,P)];calls=[]
    if not P:return 1,stores,calls
    calls.append(('fill',P,255,256))
    for i in range(3):
        page=A+256*i;stores.append((P,4,page));calls.append(('page',page,64,P))
    calls.append(('release',P));return 0,stores+[(cache,4,0),(cache+4,4,0)],calls
ck(project(0)==(1,[(cache,4,0)],[]) and separate(cache,4))
count=0
for p in range(0x200043b4,0x2000b184-256+1,4):
    rc,wr,cs=project(p);ck(rc==0 and [x for x,_,_ in wr]==[cache,p,p,p,cache,cache+4]);ck(all(separate(x,n) for x,n,_ in wr));ck(separate(p,256) and [v for _,_,v in wr[1:4]]==[0x08077c00,0x08077d00,0x08077e00]);ck(all(separate(addr,words*4) for _,addr,words,_ in cs[1:4]) and cs[-1]==('release',p));count+=1
ck(not separate(slot-1,2) and not separate(slot+3,2) and separate(slot-4,4) and separate(slot+4,4))
print(f'PASS: null return; {count} aligned 256-byte placements; both slot boundaries checked')
```
