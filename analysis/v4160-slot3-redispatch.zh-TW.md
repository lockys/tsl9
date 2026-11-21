# 槽 3：重新分派不是以取消碼選路

`0x606f0` 輪詢返回後，僅考慮 a0 尚未覆寫、也沒經 `0x60708` 呼叫的分支。`0x60702` 取樣後必須不等於 165 才跳過該呼叫；`0x6070c` 再取樣，必須等於 166 才跳回 `0x60548`。回到迴圈頂端會**第三次取樣**。三條是相同的 WCH 壓縮載入（`3c24`，基址 s0、目的 a5）；不能拿上一次比較的 166 取代下一次載入。

- 若保持入口設定的 s2–s6，且從第二次到第三次讀取間位置與值均未變，第三次仍為 166，經 `0x6062c` 落入 `0x60630`，再次輪詢。若正常返回，先前核對的 [`0x6067c` 兩條續路](v4160-poll-returns.zh-TW.md)都先**覆寫**取消碼（取 s0 或常數 1），沒有先讀它。
- 若第三次讀到不同值，162、161、164、165 各有不同分支，其餘 251 個值匯入 `0x605c8`。在所分析的重新分派圖上，首次觸及 a0 或轉出本段共八個端點：兩處覆寫、一處返回、五處轉移，沒有讀取舊 a0 的端點。配合[呼叫目標分析](v4160-slots34-direct-transfers.zh-TW.md)，輪詢可保留 a0，尾跳或返回也不等於已消費它。若再次回到本迴圈，上述分派規則重用；不主張迴圈或外設等待一定結束，也不主張裝置實際採用此參考碼。

重現：於 repo 根目錄以 V1.31 carrier 為參數執行。分派模型由五條實際條件跳轉解碼；八端點另用既有受限指令遍歷器檢查。

```python
from pathlib import Path
from hashlib import sha256
from runpy import run_path
import sys
b=Path(sys.argv[1]).read_bytes();m=run_path('analysis/check_v131_slots34.py');ck,sx,walk=(m[k] for k in ('ck','sx','walk'))
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p):return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
R={}
for p in range(0x60530,0x60544,4):
    x=w(p);ck((x&0x000ff07f)==0x13);R[x>>7&31]=sx(x>>20,12)
ck(R=={21:162,19:161,18:166,22:164,20:165})
def edge(p,v):
    x=w(p);f=x>>12&7;ck(x&127==99 and x>>15&31==15 and f in (0,1));d=x>>31<<12|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    return p+sx(d,13) if (v!=R[x>>20&31])==bool(f) else p+4
ck(all(w(p)&65535==0x243c for p in (0x60702,0x6070c,0x60548)))
branches={0x6054a,0x6060e,0x6062c,0x606e4,0x60714};table={162:0x6054e,161:0x60612,166:0x60630,164:0x606e8,165:0x60708}
for v in range(256):
    ck(edge(0x60704,v)==(0x60708 if v==165 else 0x6070c));ck(edge(0x6070e,v)==(0x60548 if v==166 else 0x60712))
    p=0x6054a
    for _ in range(5):
        if p not in branches:break
        p=edge(p,v)
    ck(p==table.get(v,0x60718)) # 60718: compressed jump to 605c8
ck(w(0x60718)&65535==0xbd45)
ck(walk(b,0x60548,0x60754)==[(0x60596,'transfer'),(0x605e0,'transfer'),(0x6061a,'overwrite'),(0x60678,'transfer'),(0x606ec,'transfer'),(0x60708,'transfer'),(0x60734,'overwrite'),(0x60752,'ret')])
print('PASS: 256 states, two back-edge guards, fresh dispatch read, 8 first-use/exit endpoints')
```
