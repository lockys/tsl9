# 第 13 列：整表初始化、單列更新與讀取

固定 APP 的第 13 列佔 `[0x2000c254,0x2000c260)`。已核對兩種目的範圍含該列的服務請求，不能把兩者都當作延遲回呼期間的寫入：

- `0x12d92` 初始化例程第二次間接呼叫（`0x12dbe`）傳入 `(0x2000c1b8,0,228)`；若第一次服務返回並保存 s0，且第二次服務按 fill 語意完成，會清空整張 19 列表，包括第 13 列。這不是回呼登記之後又執行過初始化的證據。
- mode 1 的另一筆 ID 1001 若再次走到 `0x15234`，會再請求複製 12 bytes 到同一列。不需假定另一個寫入函式就能解釋為何稍後讀到不同記錄；但到達順序、服務完成和實際更新均未觀測。
- `0xfdcc` 與先前的 `0xfd48` 一樣使用方向 **1**，是從第 13 列讀到本地，而非回寫。`0xfd86/0xfd8a` 另有直接 byte 讀：`0x2000c257` 正是列偏移 +3；隨後取低兩位，用於選擇寫入 `gp+290` 的值，並未寫回該列。

下列重播區分資料讀取、地址形成與寫入。掃描只涵蓋半字邊界連續兩條 32-bit 指令（LUI/AUIPC 接同基底 load/store/ADDI，計算的起址落入列內），並非完整寫入者清單；不排除透過其他基址、間接指標或跨界範圍更新。

```python
from hashlib import sha256
from pathlib import Path
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('row13 evidence mismatch')
def u(i): return int.from_bytes(b[i:i+4],'little')
def pin(p,h):
    s=bytes.fromhex(h);ck(b[p-32768:p-32768+len(s)]==s)
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
pin(0x12d96,'370404003c4406d61306001881451795ff1f1305452982973c441306400e81451795ff1f130525408297')
a=0x12db6+(u(0x12db6-32768)&0xfffff000)+(u(0x12dba-32768)>>20);size=u(0x12db0-32768)>>20
ck((a,size,a+13*12,a+size)==(0x2000c1b8,228,0x2000c254,0x2000c29c))
pin(0x1522e,'b54501452286ef304f87');pin(0xfdc2,'5000b5450545a380f112ef80cfcd');pin(0xfd8e,'0d8b8547e317f7fe8947e5b7')
hits=[]
for i in range(0,len(b)-7,2):
    v,w=u(i),u(i+4);op=w&127
    if v&127 not in (23,55) or op not in (3,19,35) or (v>>7&31)!=(w>>15&31): continue
    if op==19 and (w>>12&7)!=0: continue
    imm=(w>>25<<5|w>>7&31) if op==35 else w>>20
    dst=((i+32768 if v&127==23 else 0)+(v&0xfffff000)+(imm^2048)-2048)&0xffffffff
    if a+156<=dst<a+168: hits.append((i+32768,dst,op,w>>12&7))
ck(hits==[(0xfd86,0x2000c257,3,4)])
print('PASS: 19-row fill includes row13; opposite copy directions; direct address-pair scan: 1 LBU, 0 stores')
```
