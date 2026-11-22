# 取消之前：六輪設定各要求六次傳輸，傳輸逾時不會提前退出

範圍是[索引 1、2 的讀回路徑](v4160-selector-reload-branches.zh-TW.md)，不是 selector 0 的 14 筆迴圈。`0x16d4c` 每輪讀取一個小端半字 `H`，`0x16d7e` 呼叫 `0x168de(selector, reg, &payload[0], 4)`。六輪的 reg 依序為 **`00 04 08 10 14 18`**（十六進位）；不是從 0 起連續編號。payload 是 `[(H & 0x7ff) >> 3, (H << 5) & 255, 0, 0]`。若先前的 12-byte 填零與 2-byte 複製如要求完成，且中途未改來源，這條呼叫鏈六個 H 都為零。

`0x168de` 每輪先依 selector 1 或 2 對控制位址寫 16 或 1，再依序以 **2、reg、四個 payload bytes** 呼叫 `0x16896`。第六次正常返回後對另一控制位址寫 17 並返回。兩層迴圈的繼續條件分別是指標未到末端及輪數未到 6，都不是測傳輸返回值。因此若兩段 ready 輪詢任一逾時並正常返回零，仍會做下一次；這 **36 次是呼叫數，不是 36 次成功送出**。第一段逾時連資料暫存器也沒寫，第二段逾時則已經寫了。上述次數以存取成功、正常返回且保存的暫存器與棧資料未被外部改寫為限。後面還有 `0x169dc(selector,0)`，須正常返回才到取消 helper。

離線核對（repo 根目錄，Python）：由原指令解出六個 reg、遮罩及位移，對所有 16-bit H 核對封包，並核對內外計數分支與三個傳輸呼叫點。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('six-transfer evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def u(p,n=4): return int.from_bytes(b[p-32768:p-32768+n],'little')
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
def imm(p): return ((u(p)>>20)^2048)-2048
def jal(p):
    w=u(p); ck(w&4095==0xef); d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    return p+(d^1048576)-1048576
ck([jal(p) for p in (0x1690c,0x16916,0x16938,0x16d7e,0x16d8a,0x16d92)]==[0x16896]*3+[0x168de,0x169dc,0x16858])
pin(0x16d34,'b70a0810096a'); pin(0x16d42,'938a0a40130a4a81194b'); pin(0x16d4c,'83d7040056c62318410193f7f77f13d737009607a304f100'); pin(0x16d64,'7c00ca9783c5070091463000228505092304e100231501008904'); pin(0x16d82,'e31569fd')
regs=((u(0x16d34)&0xfffff000)+imm(0x16d42)).to_bytes(4,'little')+(((u(0x16d38,2)>>2&31)<<12)+imm(0x16d46)).to_bytes(2,'little'); ck(regs.hex()=='000408101418')
for h in range(65536):
    x=h&imm(0x16d56); pair=bytes([x>>(u(0x16d5a)>>20),(x<<(u(0x16d5e,2)>>2&31))&255]); ck(pair==((h%2048)*32).to_bytes(2,'big'))
pin(0x16908,'09452ec6'); pin(0x16910,'b245a2942e85'); pin(0x1691a,'631c9400'); pin(0x16932,'034504000504'); pin(0x1693c,'f9bf'); pin(0x168d0,'01458280'); pin(0x168dc,'d5bf')
print('PASS: six register selectors; 65536 payload pairs; six direct call targets')
```
