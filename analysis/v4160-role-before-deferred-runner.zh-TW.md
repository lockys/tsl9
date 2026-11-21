# 首次角色讀取前：回呼入口已登記，不代表回呼已執行

接續[建節點回呼的兩個槽](v4160-first-node-upstream-slots.zh-TW.md)。此處區分三件事：安裝處理函式、進入處理函式、執行已排定的回呼。下列 RAM 位址均假設 V1.31 參考程式按正常啟動路徑搬移，並非設備觀測。

1. 啟動函式 `0x6de0c` 在 `0x6de3c` 把 **入口** `0x20002e34` 寫到 `0x20000008`。這是一次資料寫入，比第一次角色初始化早；不是執行入口，也沒有把建節點函式 `0x5c9b4` 寫到回呼槽。後者的槽 `0x20002ef8` 與旗標 `0x20002efc` 在正常啟動清零時都被清除。
2. 若進入該入口，來源 `0x430a4..0x430b4` 以 PC 相對位址先讀旗標，再無條件將它清零，**依原讀值**分支。原值為零時繞過本段安排回呼的指令（另一條路徑另有子呼叫，並非證明全無副作用）。非零路徑則將 `mepc` 設為 `0x20002e28`，中間呼叫 `0x42dbc` 的搬移版本；若正常返回、`mepc` 保持且 `mret` 如預期生效，`0x20002e28` 的 JAL 才進 `0x200007a0`。
3. runner **重新讀回呼槽，不是重讀旗標來決定是否呼叫**。槽為零跳過間接呼叫；若此刻仍是 `0x5c9b4`，才由這條路徑呼叫建節點的上游函式。返回後再次讀旗標，再決定是否清槽。首次 `0x55bde` 前是否出現入口執行、旗標非零及該槽值，仍沒有時序證據。

重現：以 V1.31 carrier 為唯一參數。檢查搬移前後的同一條 JAL、兩個 PC 相對位址、兩級分支與啟動 store。這不是 IRQ、CSR 或 callback 的執行測試。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes();base=0x40000
def ck(ok):
    if not ok:raise ValueError('deferred runner evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
def w(p):return int.from_bytes(b[p-base:p-base+4],'little')
def ram(p):return p-0x40270+0x20000000
def imm(w):return (w>>20^2048)-2048
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x6de14,'b7070020');raw(0x6de28,'37370020130747e3');raw(0x6de3c,'98c7');ck((w(0x6de28)&0xfffff000)+imm(w(0x6de2c))==ram(0x430a4))
raw(0x430a4,'970200009382820c0383020023800200630f0300');raw(0x430be,'970500009385a5fd73901534eff03fcf73002030');ck(ram(0x430a4)+imm(w(0x430a8))==0x20002efc and ram(0x430be)+imm(w(0x430c2))==ram(0x43098))
x=w(0x43098);v=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==239 and ram(0x43098)+(v^0x100000)-0x100000==ram(0x40a10)==0x200007a0)
raw(0x40a10,'b737002003a787ef');raw(0x40a22,'11c30297');raw(0x40a2a,'83c7c7ef93f7f70f99e323200400');ck(0x20003000+imm(w(0x40a14))==0x20002ef8)
print('PASS: early entry pointer; read-before-clear flag; relocated resume and runner; separate callback slot')
```
