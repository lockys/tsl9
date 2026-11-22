# 三次查表共用同一張表：清掉第一筆不會改變下一個鍵的位置

在 `0x12aa0` 保存 selector、呼叫 `0x1070a` 再讀回的路徑，三次 `0x90b0` 搜尋的回呼地址依序是 **0x1061c、0x9b36、0x107c0**。它們互異且都不是零。每次從第 0 列重新找，至多看 15 列；若命中，只清第一個匹配列的 `+4/+8`，沒有壓縮表或搬移後續列。即使表內有重複鍵，後面的同鍵列也保留。因此每次命中的列號（或未命中）都可以直接從**入口時的表**算出：把先前的鍵改成零，不可能消滅或製造另一鍵的匹配。

這個推論需要三次搜尋及中途服務正常返回、無並行改表，且[釋放](v4160-selector-release-separation.zh-TW.md)與[取消](v4160-selector-cancel-separation.zh-TW.md)的資料寫址不碰列及 selector；服務與呼叫者的有效棧框也須分離。名義 arena 在列之前；[兩次填零及旗標寫入](v4160-selector-save-no-match.zh-TW.md)亦不碰兩者。符合這些條件時，三次搜尋即使有命中，`0x12aaa` 讀回的仍是入口保存的完整 word，不是最後一次取消的返回狀態。不是實機上表的快照，也不表示事件已執行。

重播（repo 根目錄，Python）。固定原 APP，檢查搜尋鍵、清欄與棧讀回指令。用一份可變的表依序執行，和直接由初始表算出的三個最低列號及完整最終表比對；列舉所有合法的首筆位置組合，再加重複鍵案例。這是列操作的投影，不是 provider 或 CPU 模擬。

```python
from pathlib import Path
from hashlib import sha256
from itertools import product
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('three lookup mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def seg(pc,n): return b[pc-32768:pc-32768+n]
def addr(pc):
    a=int.from_bytes(seg(pc,4),'little'); i=int.from_bytes(seg(pc+4,4),'little',signed=True)
    ck(a&4095==0x517 and i&0xfffff==0x50513); return (pc+(a&0xfffff000)+(i>>20))&0xffffffff
keys=tuple(addr(pc) for pc in (0x10624,0x10730,0x1073e)); ck(keys==(0x1061c,0x9b36,0x107c0))
ck(seg(0x12aa0,12).hex()=='01112ac606ceefd05fc63245' and seg(0x9110,8).hex()=='0504b107e319e4fa')
ck(seg(0x90fe,8).hex()=='23a2040023a40400')
def run(tags):
    src=[(j+40,k,101+j) for j,k in enumerate(tags)]; live=src.copy(); seen=[]
    for key in keys:
        for j,(_,k,_) in enumerate(live):
            if k==key:
                live[j]=(live[j][0],0,0); seen.append(j); break
        else: seen.append(None)
    expected=[next((j for j,k in enumerate(tags) if k==key),None) for key in keys]
    ck(seen==expected and live==[(t[0],0,0) if j in expected else t for j,t in enumerate(src)])
n=0
for pos in product(range(-1,15),repeat=3):
    occupied=[p for p in pos if p>=0]
    if len(set(occupied))!=len(occupied): continue
    tags=[7]*15
    for k,p in zip(keys,pos):
        if p>=0: tags[p]=k
    run(tags); n+=1
    for j in range(15):
        opts=[k for k,p in zip(keys,pos) if 0<=p<j]
        if j not in occupied and opts: tags[j]=opts[j%len(opts)]
    run(tags)
ck(n==3406); print('PASS:',n,'first-position combinations; two shared-table runs each')
```
