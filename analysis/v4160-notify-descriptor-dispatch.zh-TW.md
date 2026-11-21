# 非零延遲通知：派發的是槽內現存的描述項

承接[描述項來源](v4160-notify-descriptor-source.zh-TW.md)。兩處 APP 都要求 `0x9124(0x13f36,0,10或100,D)`。排程表與派發表的 PC 相對位址同為 `0x2000be08`，15 筆，每筆 12 bytes。非零延遲先比對回呼位址，不比對 D 或表標記。

- **相同回呼已存在**：取第一個匹配槽 `+8` 的舊參數，非零就先交給 `[0x40068]`；正常返回且所需暫存器保持時，`0x91cc` 將入口 a3 經 s4 寫回同一槽 `+8`。此分支不重寫 `+4`。所以兩個不同通知若在派發前先後登記，第二個可取代第一個，即使還有空槽。
- **沒有匹配**：第二輪掃描找首個空槽，寫 `+4=0x13f36`、模式 byte `=0`、`+8=D`。若 15 槽皆滿且無匹配，返回 1，不寫入本次 D。
- **請求事件**：上述兩種成功選槽的路徑都是先寫表，再用 `gp+166` 的 task byte、`1<<index` 和換算值 `16/160` 呼叫 `[0x40058]`。此處不直接呼叫 `0x13f36`，且已寫表不等於事件成功。
- **派發**：`0x901a` 按低位優先選取事件遮罩中的槽（0..14）。讀 `+4` 至 a3，非零才讀模式與 `+8` 至 a0。模式零時先清掉 `+4/+8`，再 `0x9058: jalr a3`；清的是槽，不是暫存器或描述項。因此若真的選到該槽，且兩個欄位自最後一次登記後均未變，回呼取得的就是**最後登記的 D**。若在派發前替換，不能把第一次登記與這次回呼視作同一個描述項。

以下檢查可從本文抽出以 Python 執行，參數為原 decoded BIN。它驗證三個基址計算、實際 slot word 存取的操作數，以及模式零時先載入、再清除、最後呼叫的順序。另重跑 `experiments/v4160-scheduler-mode-width/match_update.py` 驗證既有匹配路徑。這些是離線指令和有限案例，未執行 resident 排程服務，也不證明生命週期或實機派發。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
if sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP')
def ins(p,n): return int.from_bytes(b[p-0x8000:p-0x8000+ n],'little')
for p,r in ((0x9132,18),(0x9188,15),(0x9034,15)):
    u,i=ins(p,4),ins(p+4,4)
    if u&4095!=r<<7|23 or i&0xfffff!=r<<15|r<<7|19: raise ValueError('pair')
    if p+(u&0xfffff000)+(i>>20 ^ 2048)-2048!=0x2000be08: raise ValueError('base')
def csw(p,store,rd,off):
    w=ins(p,2)
    return (w&0xe003)==(0xc000 if store else 0x4000) and 8+(w>>7&7)==15 and 8+(w>>2&7)==rd and ((w>>10&7)*8+(w>>6&1)*4+(w>>5&1)*64)==off
for p,store,r,off in ((0x91aa,0,10,8),(0x921c,1,10,4),(0x9040,0,13,4),(0x9048,0,10,8)):
    if not csw(p,store,r,off): raise ValueError(hex(p))
for p,r,off in ((0x91cc,20,8),(0x9222,20,8),(0x9050,0,4),(0x9054,0,8)):
    if ins(p,4)!=(r<<20|15<<15|2<<12|off<<7|0x23): raise ValueError(hex(p))
for p,w in ((0x9190,0x8a36),(0x904e,0xe709),(0x9058,0x9682)):
    if ins(p,2)!=w: raise ValueError(hex(p))
print('PASS: common table base; 8 slot accesses; saved argument and clear-before-call sites')
```
