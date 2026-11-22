# 命中回呼列：先處理附帶指標，再清列並取消該列事件

接續[未命中路徑](v4160-selector-save-no-match.zh-TW.md)。原 APP `0x90b0` 找到匹配列 `j`（0..14）時用 `row+8` 決定是否呼叫 `[0x40068]`。指標為零直接略過；非零時，若服務正常返回且保存 s0/s1，APP **不依返回狀態分支**。它清除 `row+4` 與 `row+8` 兩個 word，不清 `row+0`，然後尾跳 `[0x4005c](U8[gp+166], 1<<j)`。注意不是 `gp+363` 的設定任務。即使 `j=0` 使遮罩等於 1，這也是取消請求，不是送出事件 1。

V1.31 參考實作（不是設備 ROM 身分證據）：

* `0x40068 → 0x431ba`：非零指標的標記 byte 若不等於 255，返回 4，這個分支只有自身棧與 `0x4002420c` 控制 word 寫入。等於 255 才呼叫 RAM 例程 `0x20000110`；若正常返回，包裝函式返回 0。**返回 0 不證明堆積區一定被修改**，其寫址仍依 RAM 程式和配置狀態而定。指標為零時 APP 根本不進此服務。
* `0x4005c → 0x439a8`：查找 `(task ID, mask)` 的定時器。找到才將 `node+2` 半字清零；未找到也照樣進 `0x4358a`。若 ID 小於當前任務數，後者對 pending 表第 ID 個半字執行 `old & ~mask`。若 ID 等於執行中的任務索引，外層另將 mask OR 入 `0x200031dc` 半字，這個比較獨立於前一個 ID 容量檢查。正常時依 timer 是否命中返回 0 或 6，不代表 pending 是否發生改變。另有自身棧與控制 word 的寫入。

因此可將「命中時是否保留外層 selector」縮為具體前提：棧及控制 word 與保存位置分離，列、有效 pending 表、命中 timer 節點皆在各自資料區；若進入 RAM 釋放例程，還要確認其寫址。此處沒有觀測裝置上的表、節點或配置，不能把這些前提當成已成立。

可重播核對（repo 根目錄，Python）。固定兩映像身分、解碼 RAM 呼叫目標、核對條件寫入，並分開測試 timer 命中、ID 有效與 current 相等三個條件；是局部投影而非完整 CPU。

```python
from pathlib import Path
from hashlib import sha256
def ck(ok):
    if not ok: raise ValueError('hit effects mismatch')
a=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def pin(b,i,s): ck(b[i:i+len(bytes.fromhex(s))]==bytes.fromhex(s))
def w(i): return int.from_bytes(r[i:i+4],'little')
def pair(i): return (0x40000+i+(w(i)&0xfffff000)+(int.from_bytes(r[i+4:i+8],'little',signed=True)>>20))&0xfffffffe
pin(a,0x10d4,'884709c5b7070400bc578297'); pin(a,0x10e6,'8545b39585002244b240c20503c5610ac181be94b707040023a2040023a4040003a3c705')
ck((w(104),w(92),pair(0x31f8),pair(0x39c8))==(0x431ba,0x439a8,0x20000110,0x20000314))
pin(r,0x31e4,'0347e5ff9307f00f6306f700232694201145d5b7'); pin(r,0x39d2,'19c123110500a2854a857d36'); pin(r,0x39e2,'83c7c71963992701b737002003d7c71d598c239e871c'); pin(r,0x35b2,'93c5f5ff3a951a21f98d0ea1'); pin(r,0x3a00,'014591e01945')
def cb(i,value):
    h=int.from_bytes(r[i:i+2],'little'); ck(h&3==1 and h>>13 in (6,7))
    v=sum((h>>s&1)<<d for s,d in zip((12,11,10,6,5,4,3,2),(8,4,3,7,6,2,1,5)))
    return i+(v^256)-256 if ((value!=0)==(h>>13==7)) else i+2
n=0
for j in range(15):
    m=1<<j
    for hit in (False,True):
        node=0x20005000 if hit else 0
        ck(cb(0x39d2,node)==(0x39d4 if hit else 0x39d8))
        ck(cb(0x3a02,node)==(0x3a06 if hit else 0x3a04))
        for valid in (False,True):
            for current in (False,True):
                for old in (0,65535,m,65535^m,0x5555,0xaaaa):
                    pending=old&~m if valid else old; cancel=old|m if current else old
                    ck((pending^old)==(old&m if valid else 0) and (cancel^old)==(m&~old if current else 0)); n+=1
print('PASS: both service targets and RAM calls; 15 row masks;',n,'conditional mask cases')
```
