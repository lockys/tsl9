# 命中回呼列後釋放：正常區塊標頭與 selector 棧槽分離

[命中列分析](v4160-selector-hit-effects.zh-TW.md)留下的 RAM 呼叫是 `0x431f8 → 0x20000110`。若 `0x40068` 及 RAM 程式均為 V1.31 參考版本，採用其啟動複製映射與 Xwchc 解碼，則可用[釋放函式的 11 個 store](v4160-44098-release-write-set.zh-TW.md)核對這個呼叫點，不必假設定長清零整個 payload。

* **這個呼叫點能排除一筆計數器寫入。** 設 P 是列的非零附帶指標，H 是釋放程式實際選中的區塊標頭。若 P 正是 H+8，且兩次讀取間標頭未變，外層通過條件 `U8[P-2]==255` 就代表 `U16LE[H+6]` 的低 byte 為 255，不可能等於內層特殊值 `0x8001`。因此不會執行 `0x20000168` 的計數器遞增。這不是所有釋放呼叫都跳過該分支的證明。
* **棧槽分離不依賴是否合併區塊。** 釋放程式的五個動態 store 均落在被更新的 8-byte 標頭內；另有固定的控制 word 與配置統計欄位。若所有實際更新的標頭完整落在名義 arena `[0x200043ac,0x2000b184)`，則向前或向後合併都不會越出這個寫入範圍。沿[先前的高位棧案例](v4160-selector-save-no-match.zh-TW.md)，`0x12aa0` 的入口 SP 為 E，保存槽是 `[E-20,E-16)`，位於 arena 上方，也與固定寫址分離。這項範圍結論不需要 P=H+8；它需要的是有效標頭的條件。正常返回碼或單一指標的來源均不足以證明整條串列有效。

在上述條件下，這個 RAM 例程的直接 store 不改 selector；未量測實機堆積區、SP 或 MMIO 副作用。取消服務的 pending 表與 timer 節點仍須另證其當時的位置。

核對片段（從 repo 根目錄執行）。對照 carrier 的完整函式指紋，解碼兩層標記比較，逐一核對標頭 store 的位移、寬度，再檢查記憶體區間。

```python
from pathlib import Path
from hashlib import sha256
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('release separation mismatch')
def w(i): return int.from_bytes(r[i:i+4],'little')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' and sha256(r[0x380:0x454]).hexdigest()=='a510cc84e9173549d7f5b68da894f5b5ba9109bcd0c2601653bbdf0f5c964c50')
ck(r[0x31e4:0x31f0].hex()=='0347e5ff9307f00f6306f700' and r[0x31f8:0x3200].hex()=='97d0fb1fe78080f1')
i=0x270+0x154; h=w(i)&65535
ck((h&3,h>>13,8+(h>>7&7),8+(h>>2&7),8*(h>>10&7)+2*(h>>5&3))==(2,1,15,12,6))
ck(r[i+2:i+10].hex()=='216705076319e600'); tags=[t for t in range(65536) if t&255==255]; ck(len(tags)==256 and 0x8001 not in tags)
fields=[]
for pc in (0x178,0x19e,0x1a8,0x1ce,0x1d0):
    v=w(0x270+pc); h=v&65535
    if h&3==3:
        ck(v&127==35); fields.append(((v>>25)*32+(v>>7&31),1<<(v>>12&7)))
    elif h&3==2 and h>>13==5: fields.append((8*(h>>10&7)+2*(h>>5&3),2))
    else:
        ck(h&3==0 and h>>13==6); fields.append((8*(h>>10&7)+4*(h>>6&1)+64*(h>>5&1),4))
ck(fields==[(6,2),(0,4),(4,2),(4,2),(0,4)])
lo,hi=0x200043ac,0x2000b184
for d,n in fields: ck(0<=d and d+n<=8 and lo<=hi-8)
for e in range(0x2000ca00,0x20010001,16):
    for p,n in [(lo,hi-lo),(0x20002fa4,1),(0x200031a2,2),(0x4002420c,4)]: ck(p+n<=e-20 or e-16<=p)
print('PASS: 256 accepted header tags exclude 0x8001; 5 header stores; 865 aligned selector placements')
```
