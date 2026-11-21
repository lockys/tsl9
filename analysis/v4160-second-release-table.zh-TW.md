# 釋放第二塊時，合併方向決定第一塊是否保留

接續[第二次配置](v4160-second-allocation-frontier.zh-TW.md)。在相同名義初始條件下，以 `H` 表第一塊 header，`N` 表第二塊，`F` 表第二次分割出的空閒尾塊，`E` 表 sentinel。釋放前的鏈為 `小區塊 → H(已用) → N(已用，256 bytes) → F(空閒) → E`。假設回呼沒有改變 header、游標或暫存指標，且傳給 `0x20000110` 的仍是 `N+8`。

* 搜尋跳過小區塊與 H：它們的 successor 都小於 `N+8`。在 N 命中，清除 `N+6` 的 tag，把 256 加回可用量。第二次請求的 tag 為 78，不是觸發特殊計數的 `0x8001`。
* **不向前合併。** 前一塊 H 的 tag 為 1；`0x2000019a` 因 tag 非零跳到 `0x200001ae`，略過改寫前塊 header 的指令。**只向後合併。** F 不是 sentinel 或大區塊游標，tag 為零。`0x200001ce/1d0` 將 N 的容量改為 `256+8+F容量`，下一塊指向 E；`0x200001d6` 將 header 的 8 bytes 加回可用量。F 從鏈中移除，不表示其舊 bytes 被清除。
* 結果是 `H → N(空閒) → E`。第一塊的 header 與 payload 都不在這次釋放的寫入範圍；`T=H+8+576=0x200047f4` 的函式表空間也保留。**此時三個 handler 還沒寫入**：它們是在 `0x44022` 返回後才登記。此處不是證明已登記的 handler 經過釋放仍可執行。

以下是對 V1.31 參考 carrier（唯一參數）的條件模型，不是通用 CPU。核對完整釋放函式身分，按該路徑的 header 欄位順序操作合成 RAM；以非零圖樣偵測第一塊被意外覆寫，而非假定裝置內容。參見[原指令寫址](v4160-44098-release-write-set.zh-TW.md)。

```python
from hashlib import sha256
from pathlib import Path
from struct import pack_into,unpack_from
import sys
b=Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('release/table mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
need(sha256(b[0x380:0x454]).hexdigest()=='a510cc84e9173549d7f5b68da894f5b5ba9109bcd0c2601653bbdf0f5c964c50')
s,h,e=0x200043ac,0x200045ac,0x2000b184
for c in range(256):
    k=14+3*((c>>2)+(c&3)); r=(576+6*k+3)&~3
    n=h+8+r; f=n+8+256; mem=bytearray([0xa5])*(e-s)
    def head(p): return unpack_from('<IHH',mem,p-s)
    for p,q,tag in [(s,h,0),(h,n,1),(n,f,78),(f,e,0)]: pack_into('<IHH',mem,p-s,q,q-p-8,tag)
    before=mem[h-s:n-s]; p=s; prev=None; path=[]; ptr=n+8
    while p<e:
        q,cap,tag=head(p); path.append(p)
        if p<=ptr<=q: break
        prev,p=p,q
    need(path==[s,h,n] and p+8<=ptr and tag==78 and prev==h)
    pack_into('<H',mem,p-s+6,0); need(head(prev)[2]!=0)
    q=head(p)[0]; need(q not in (h,e) and head(q)[2]==0)
    succ,tail,_=head(q); pack_into('<H',mem,p-s+4,cap+8+tail); pack_into('<I',mem,p-s,succ)
    t=h+8+576
    need(t==0x200047f4 and t+4*k<=n and mem[h-s:n-s]==before)
    need(head(h)==(n,r,1) and head(n)==(e,e-n-8,0))
print('PASS: 256 layouts; next-only merge; first header and payload unchanged')
```
