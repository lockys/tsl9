# 取消服務：待處理事件與定時器的寫址是否碰到 selector？

接續[命中列](v4160-selector-hit-effects.zh-TW.md)與[釋放例程](v4160-selector-release-separation.zh-TW.md)。以下限 V1.31 參考映射、Xwchc、正常存取與無外部干擾。

* **待處理事件表不是另一次配置。** `0x43be2..0x43bfc` 重新讀取 payload 指標 P 與容量 K，將 `P+576` 存為 handler 表，`P+576+4*K` 存為 pending 表。若 P 與 K 保持[配置時](v4160-second-allocation-frontier.zh-TW.md)的值且表指標未改，對 `ID<count<=K`，取消服務的半字寫入完全落在原請求 `[P,P+576+6*K)` 內。僅有 `ID<count` 不足以確定所有權。名義 `P=0x200045b4,K=29` 時，pending 是 `[0x20004868,0x200048a2)`，ID 7 的欄位正是另一條[送事件路徑](v4160-id7-queue-pending-post.zh-TW.md)的 `0x20004876`。
* **定時器不是按任務 ID 索引的固定陣列。** `0x20000314` 從 `0x200031e8` 取首節點，沿 `+12` 查找 event 和 ID 都相等的節點；返回零時不寫節點。非零時呼叫者只清 `node+2` 半字，並非清除整個節點。只要命中的是仍有效、完全在 arena 的 16-byte timer，該寫入便在 arena 內；不能只憑第一個 timer 曾配置成功就假定之後的整條串列有效。

故在上述前提、兩塊資料均在名義 arena、入口 SP 屬於先前的高位對齊案例時，兩筆動態寫入與 `[SP-20,SP-16)` 分離。固定的 `0x200031dc` 取消遮罩及 `0x4002420c` 控制 word 也不重疊。不要求 timer 一定命中，也不表示真機的 count、表指標或 SP 已知。

重播（repo 根目錄，Python）。固定 carrier 與四個原指令窗；列舉容量來源與合法 ID，並比對 arena、固定寫址與 865 個棧位置。不是 CPU 執行軌跡。

```python
from pathlib import Path
from hashlib import sha256
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('cancel separation mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for off,code in [(0x3be2,'83a7c4223820b7340020938707240a0723a2f41cba97373700202322f71e'),(0x584,'b737002083a7871e99e33e858280ba236315b7009823e30aa7fedc47f5b7'),(0x39d2,'19c123110500'),(0x35aa,'131715000325461e93c5f5ff3a951a21f98d0ea1')]:
    s=bytes.fromhex(code); ck(r[off:off+len(s)]==s)
p=0x200045b4; lo,hi=0x200043ac,0x2000b184; n=0
for c in range(256):
    k=14+3*((c>>2)+(c&3)); base=p+576+4*k; end=p+576+6*k
    for i in range(k):
        start=base+2*i; ck(lo<=base<=start and start+2<=end<=hi); n+=1
    if c==14: ck((k,base,end,base+14)==(29,0x20004868,0x200048a2,0x20004876))
for node in range(lo,hi-15): ck(lo<=node+2 and node+4<=hi)
for sp in range(0x2000ca00,0x20010001,16):
    for a,b in [(lo,hi),(0x200031dc,0x200031de),(0x4002420c,0x40024210)]: ck(b<=sp-20 or sp-16<=a)
print('PASS:',n,'capacity/ID pairs; valid timer extents; 865 stack positions')
```
