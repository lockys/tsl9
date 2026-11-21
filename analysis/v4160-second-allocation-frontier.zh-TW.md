# 第二次配置：失敗回呼與正常 heap 分開判斷

範圍是 v4.1.60 APP 配 V1.31 參考 ROM，從 `0x43bbe` 到讀回不一致後的 `0x4406a`。這是兩次**不同**的配置呼叫；兩者的 AUIPC/JALR 都算到複製後的 `0x20000040`。

* **失敗回呼槽。** 從[第一次配置入口為零](v4160-role-first-allocation-prefix.zh-TW.md)出發，只有第一次成功才走到第二次。有效 header 的[分割與記帳](v4160-role-allocator-metadata.zh-TW.md)只寫 heap、統計半字、獨立 stack 與外設。`0x43bc6` 寫配置結果到 `0x2000322c`，並非 `0x20003220`。隨後清零的目的為新 payload，要求長度從容量 byte 重算；須該 byte 不變，不能僅因配置成功就認定任意 fill 都合法。其後兩個表指標寫在 `0x200031c4/31e4`，`0x4329a` 清的是 `0x20003198`。第二次配置前的[第一次讀回](v4160-handler-base-survival.zh-TW.md)只需四個 stack bytes；須回呼如所綁定、copy 限於目的、stack 分離且無其他寫入。在這些條件下，失敗回呼槽到第二次入口仍為零。配置器搜尋失敗到達 sentinel 時會**重讀**該槽；維持零才會跳過間接呼叫，不代表整條失敗路徑沒有任何 store。
* **更強的正常初始化條件。** 若 `0x43104` 建立的第一個大區塊未被其他操作配置，header `H=0x200045ac`，末端 sentinel `E=0x2000b184`，容量 `E-H-8=27600`。第一次請求對齊後為 660..1848 bytes，必分割；清零終點不越過新 header。若串列與大游標保持原樣、存取成功，第二次名義請求為 256 bytes，從 H 跳過已佔用區塊，下一塊至少還有 **25744 bytes**，不會走到 sentinel。這比「失敗時回呼為零」更強，但只適用這組初始條件，不代表裝置配置實況。

以下檢查使用 V1.31 carrier 路徑。指令窗固定至參考檔；256 組是輸入 byte 的數學列舉，不是 256 次 CPU 或硬體執行。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def need(ok):
    if not ok: raise ValueError('second allocation evidence mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def target(p):
    u,i=(int.from_bytes(b[j:j+4],'little') for j in (p,p+4)); need(u&4095==0x97 and i&0xfffff==0x80e7)
    return (0x40000+p+(u&~4095)+((i>>20^2048)-2048))&0xfffffffe
need(target(0x3bbe)==target(0x406a)==0x20000040 and target(0x3bda)==0x2000039c)
need(b[0x3158:0x3164].hex()=='1cc3998fe1175ea323130700')
need(b[0x300:0x312].hex()=='373700200327072269d3c207dd8d05450297')
need(b[0x37c:0x380].hex()=='0841bdbf')
h,e=0x200045ac,0x2000b184
rows=[]
for c in range(256):
    k=14+3*((c>>2)+(c&3)); size=576+6*k; aligned=(size+3)&~3
    n=h+8+aligned; left=e-n-8
    need(h+8+size<=n and n+8+left==e and left-256>8)
    rows.append((aligned,left))
need(min(r for r,_ in rows)==660 and max(r for r,_ in rows)==1848 and min(l for _,l in rows)==25744)
print('PASS: both allocator targets; sentinel gate; 256 first sizes; minimum remainder 25744 >= 256')
```
