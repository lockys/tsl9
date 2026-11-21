# `0x44098` 釋放暫存區：哪些欄位會被寫入？

接續[暫存區配置與迴圈](v4160-44060-temp-buffer-stores.zh-TW.md)。呼叫者交出最後一次從 `0x200031bc` 讀到的指標。V1.31 參考 carrier 的 `0x40380..0x40454` 對應到啟動複製後的 `0x20000110..0x200001e4`；以下按這個映射和 Xwchc 指令解讀。函式不是把暫存區的 256 bytes 清零：它走訪區塊串列，清標記、更新可用量，並視相鄰區塊狀態合併。

| 釋放函式內的寫入位置（RAM PC 低 12 位） | 目的與條件 |
|---|---|
| `118 / 122` | 對 `0x4002420c` 寫零，返回路徑再寫回先前讀值。並非堆積區或設定區寫入。 |
| `168` | 當命中區塊的 `+6` 半字是 `0x8001`，遞增 `0x20002fa4` 的 byte。 |
| `178 / 186` | 清除命中區塊 `+6` 標記；把區塊 `+4` 的長度加到 `0x200031a2` 半字（低 16 位）。 |
| `19e / 1a8 / 1aa` | 若與前塊合併，更新前塊 `+0` 的後繼指標、`+4` 的長度，並把省下的 8-byte header 加回 `0x200031a2`。 |
| `1ce / 1d0 / 1d6` | 若與後塊合併，更新留下的區塊 `+4` 長度及 `+0` 後繼，並再加回一個 header。 |

**判斷：** 11 處 store 中，6 處寫固定地址，5 處寫由串列找到的 header；沒有任何一處以傳入的 payload 指標作固定長度的清零。若串列保持初始化後的範圍、每個被更新的 8-byte header 均有效且完整落在 `[0x200043ac,0x2000b184)`，這 11 處直接寫入都不會碰 `0x20003220`。僅知傳入指標原本來自一次成功配置，並不足以證明上述串列條件。未把外設副作用或裝置 ROM 身分當成已證事項。

重現：以 V1.31 carrier 路徑為參數。檢查呼叫目標、完整函式身分，逐條擷取 S-type、C.SW 與 Xwchc 半字 store 的 `(PC, base, offset, width)`；暫存器編號按 RV32。標準浮點壓縮指令解讀不適用此結論。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('release evidence mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
h=b[0x380:0x454]; need(sha256(h).hexdigest()=='a510cc84e9173549d7f5b68da894f5b5ba9109bcd0c2601653bbdf0f5c964c50')
need(b[0x4096:0x40a0].hex()=='328597c0fb1fe7808007' and 0x44098+0x1ffbc000+120==0x20000110)
i=0; rows=[]
while i<len(h):
    w=int.from_bytes(h[i:i+4],'little'); c=w&65535; q=c&3; f=c>>13; pc=0x110+i
    if q==3 and w&127==35:
        d=(w>>25)*32+(w>>7&31); rows.append((pc,w>>15&31,(d^2048)-2048,1<<(w>>12&7)))
    elif q==0 and f==6:
        rows.append((pc,8+(c>>7&7),8*(c>>10&7)+4*(c>>6&1)+64*(c>>5&1),4))
    elif q==2 and f==5:
        rows.append((pc,8+(c>>7&7),8*(c>>10&7)+2*(c>>5&3),2))
    elif q in (0,2): need(f not in (5,6,7))
    i+=4 if q==3 else 2
need(i==212 and rows==[(0x118,15,524,4),(0x122,15,524,4),(0x168,12,-92,1),(0x178,15,6,2),(0x186,10,6,2),(0x19e,13,0,4),(0x1a8,13,4,2),(0x1aa,12,6,2),(0x1ce,15,4,2),(0x1d0,15,0,4),(0x1d6,12,6,2)])
def apart(a,n): return a+n<=0x20003220 or a>=0x20003224
need(all(apart(a,n) for a,n in [(0x4002420c,4),(0x20002fa4,1),(0x200031a2,2)]))
need(all(apart(a,8) for a in range(0x200043ac,0x2000b184-7,4)))
print('PASS: 212 bytes; 11 stores; 3 fixed destinations and valid arena headers exclude cfg+52')
```
