# Task 3 收到的是整個事件半字；收到不等於立即處理 0x2000

接續[到期設位](v4160-first-timer-due-post.zh-TW.md)。以下 `0x40xxx` 為 V1.31 carrier 位置，採既有 RAM 複製映射及 Xwchc 語義；`0x1995c` 等為 decoded APP 位址。只追一次正常同步呼叫，不假設掃描必會抵達 task 3。

* **選取。** `0x40a9c` 取事件表指標 P，從目前 byte 索引 `[0x2000319c]` 讀 `U16[P+2*i]`。零則遞增索引並檢查登記數；遇到非零且索引仍小於登記數才走 `0x40b54`。因此 task 3 有待處理位不保證下一次就選到它。
* **交付。** `0x40b58` 重讀半字至 a1，`0x40b5a` 清整個槽，隨後才重讀目前索引至 a0、從 `[0x200031c4]` 的函式表按 `4*a0` 取 handler，將 `0x200031dc` 半字清零後間接呼叫。若索引、表和登記保持，這才是 `0x1995c(3,整個事件遮罩)`。檢測與交付是兩次讀取，並非自動傳常數 `0x2000`。
* **APP 優先順序。** 原 APP `0x1995c` 先測 bit 15，再測 bit 0，再測 bit 13。即使收到 `0x2000` 位，只要前兩者之一也置位，本次就先處理較高優先序分支。若只有 `0x2000`（或另有較低優先位），`0x199a6` 先呼叫槽 `[0x401ec]`，再直接呼叫 `0x197b8`。兩者正常返回且保存所需暫存器時，`0x199bc` 透過 `[0x40058]` 再要求 `(U8[gp+388],0x2000,192000)`。**是重新排程，不是原一次性節點自動續期**；這裡用重讀的 task byte，不沿用入口 a0。排程返回值隨即被覆蓋，handler 返回原遮罩 XOR `0x2000`，不能當成重新排程成功的收據。
* **返回後合併。** `0x40b7c..40b98` 重讀半字遮罩 C=`U16[0x200031dc]`、目前索引及事件表。回寫 `U16[slot] = U16[slot] | (returned & ~C)`（截低 16 位）。若回呼期間另設了事件，這裡是 OR，不是用返回值取代新事件；仍以指標有效、無穿插寫入為條件。

核對（decoded APP、V1.31 carrier）：固定交付和回寫指令，解碼 Xwchc 讀寫的基址、目的暫存器與寬度，從 APP 的符號分支移位數推導 bit，窮舉所有帶 bit 13 的半字。這是分支與局部資料流檢查，不是設備 trace。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('task dispatch mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def win(buf,p,s): ck(buf[p:p+len(bytes.fromhex(s))]==bytes.fromhex(s))
def compressed(p):
    x=int.from_bytes(b[p:p+2],'little'); return x>>13,x&3,8+(x>>7&7),8+(x>>2&7),8*(x>>10&7)+2*(x>>5&3)
ck([compressed(p) for p in (0xab0,0xb58,0xb94,0xb98)]==[(1,2,13,13,0),(1,2,14,11,0),(1,2,14,15,0),(5,2,14,10,0)])
win(b,0xb5a,'231007000345c419b737002083a7471c13172500b73a0020ba979c43239e0a1c8297'); win(b,0xb7c,'83d7ca1d0347c41993c7f7ff7d8d9317170003a7491e3e971e235d8d0aa3')
win(a,0x1198c,'93f7150013c51500fdf79397250163d40702'); win(a,0x119a2,'83a7c41e8297eff01fe1bc4c37f60200130606e0896503c5411882970965c1b7')
def shift(p): return (int.from_bytes(a[p:p+4],'little')>>20)&31
ck(shift(0x1195e)==16 and shift(0x11996)==18 and 0x2f000-512==192000)
counts=[0,0,0]
for mask in range(65536):
    if mask&0x2000:
        group=0 if (mask<<16)&0x80000000 else 1 if mask&1 else 2
        counts[group]+=1
        if group==2: ck((mask<<18)&0x80000000 and mask^8192==mask&~8192)
ck(counts==[16384,8192,8192]); print('PASS: dispatch/merge halfwords; 32768 masks with bit 13: priority groups',counts)
```
