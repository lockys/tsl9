# 三個表快照共用的 APP 呼叫框架

三個設定更新分支都在同一個 192-byte 調度框架內。沿 `0x8a48 → 0x14056` 這條同步呼叫邊，設 `S` 為入口接收程式執行 `0x88e4` **之前**的 SP。正常呼叫返回時保持 SP，且沒有跳入其他函式框架的前提下：

|步驟|SP 或寫入區間|
|---|---|
|`0x88e4` 建接收框架，`0x8a48` 呼叫調度器|`S−64`|
|`0x14056` 建調度框架；`0x14b1c / 0x14c22 / 0x14bf6` 擇一呼叫快照包裝|`S−256`|
|三個包裝各再減 272，要求複製 256 bytes 到 SP|`[S−528,S−272)`|

這是三種**替代**路徑，不是三層快照。對兩個 APP 函式區間逐條以 RV32 解碼，顯式改寫 SP 的只有上述減法及各自 `ret` 前的加法。線性盤點不證動態可達性，也不證每個間接呼叫確實還原 SP。

一個足夠但非必要的排除條件：如果整段快照位於 [reset 清零區](v4160-event4-init-bulk.zh-TW.md)的上界 `0x2000c958` 或更高，則四個任務 ID 均在快照下方。對 16-byte 對齊且不高於 reset SP 的 S，`0x2000cb70 ≤ S ≤ 0x20010000` 全都滿足。這不是已測得的入口 SP 或最大堆疊深度，也不能推論其他呼叫者。尚需追查接收入口由何處呼叫，以及當時的堆疊來源。

重現（參數：decoded APP、rasm2 執行檔；搭配[包裝原指令檢查](v4160-task-id-copy-destinations.zh-TW.md)）。不執行韌體。

```python
import hashlib,re,subprocess,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('frame evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
D={}
for start,end in [(0x88e4,0x8a52),(0x14056,0x14c8a)]:
    code=b[start-0x8000:end-0x8000]; p=start
    out=subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-D','-s',hex(start),code.hex()],text=True)
    for line in out.splitlines():
        addr,n,raw,ins=line.split(None,3); n=int(n)
        ck(int(addr,16)==p and n in (2,4) and bytes.fromhex(raw)==code[p-start:p-start+n] and ins!='invalid'); D[p]=ins; p+=n
    ck(p==end)
sp={k:v for k,v in D.items() if re.match(r'\S+ sp,',v)}
ck(sp=={0x88e4:'addi sp, sp, -64',0x895e:'addi sp, sp, 64',0x14056:'addi sp, sp, -192',0x140a2:'addi sp, sp, 192'})
for k,t in [(0x8a48,0x14056),(0x14b1c,0x12e54),(0x14c22,0x12f48),(0x14bf6,0x13052)]: ck(D[k]==f'jal ra, {t:#x}')
ck(D[0x8960]==D[0x140a4]=='ret')
ids=[0x20004000+x for x in (148,152,166,363)]
lo=(0x2000c958+528+15)&~15; ck(lo==0x2000cb70)
ss=range(lo,0x20010001,16)
for s in ss: ck(s-528>=0x2000c958 and all(not s-528<=x<s-272 for x in ids))
print(f'PASS: {len(D)} instruction starts; 4 explicit SP adjustments; 4 call edges; {len(ss)} conditional placements')
```
