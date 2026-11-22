# 取消返回後：a0 可傳回更上層，但不是 `0x12b24` 的分流依據

接[兩次輪詢](v4160-selector-poll-chain.zh-TW.md)。selector 1/2、動作 0 時，`0x16894` 是 `jr t1` 而非帶 link 的呼叫；服務正常返回時直接回到 `0x16d96`。這段與 `0x16dcc` 的兩個 epilogue 都不讀寫 a0；`0x12aa0` 原是尾跳，沒有另一層指令來轉譯返回碼。因此取消服務留下的完整 a0 能回到 `0x12aa0` 的呼叫者。V1.31 參考取消服務返回的 0/6 是 timer 命中狀態，不是先前輪詢的 0/1。

* `0x12b36` 呼叫之後立即 `li a0,2`，第一個返回值丟棄。`0x12b3c` 的第二個返回值則要分情況：`0x12b42` 比較的是 `0x12b24` **入口保存到 s0 的值**與 6，不是比較 a0。若 s0 無號大於 6，直接返回，a0 原樣往上傳。若 s0 為 0..6，用 `0x1a680` 的七個有號相對位移跳轉；七路都在使用舊 a0 前覆寫它。輸入 1 有一個細節：先進入 `0x1299e`，到其 `0x129ac` 才把 a0 換成 sp。
* `0x144b6` 的返回值被下一個 selector 2 覆寫；`0x144bc` 的則經 `0x14098` 的 epilogue 原樣返回。`0x14820` 的返回值在 `0x1411a` 被 s1 覆寫，再呼叫另一服務。

因此不能概括為「上層一定使用」或「一定忽略」。原樣返回也不是更高層已檢查它的證明。結論限上述直接路徑、指標及棧有效、呼叫正常返回且保存暫存器未被破壞。

重播（repo 根目錄，Python）：從原 BIN 解碼取消路徑的兩個返回序列、上界分支和七個表項，並核對第一個覆寫點與 shared epilogue。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('cancel return mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def u(p,n): return int.from_bytes(b[p-32768:p-32768+n],'little')
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
def ep(p,regs,tail):
    for j,rd in enumerate(regs):
        h=u(p+2*j,2); ck(h&0xe003==0x4002 and h>>7&31==rd and rd!=10)
    pin(p+2*len(regs),tail)
pin(0x16890,'3e8541010283'); ep(0x16d96,[1,8,9,18,19,20,21,22],'21618280'); ep(0x16dcc,[1],'05618280'); ep(0x12b7a,[1,8],'05618280'); ep(0x14098,[1,8,9,18,19],'29618280')
w=u(0x12b42,4); d=(w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
ck(w&0x707f==0x6063 and (w>>15&31,w>>20&31)==(15,8) and 0x12b42+(d^4096)-4096==0x12b7a)
pin(0x12b2a,'2a84'); pin(0x12b3a,'0945'); pin(0x12b40,'9947'); pin(0x12b4e,'0a043a941c40ba978287')
t=0x12b46+(u(0x12b46,4)&0xfffff000)+((u(0x12b4a,4)>>20^2048)-2048); ck(t==0x1a680)
ck([t+(u(t+4*i,4)^0x80000000)-0x80000000 for i in range(7)]==[0x12b58,0x12b82,0x12ba8,0x12ba8,0x12bae,0x12bc2,0x12b94])
for p,h in [(0x12b62,'2800'),(0x12ba0,'2800'),(0x129ac,'0a85'),(0x144ba,'0945'),(0x144c0,'e1be'),(0x14824,'05469305c00b6ff01f8f'),(0x1411a,'2685')]: pin(p,h)
print('PASS: 4 return sequences preserve a0; unsigned s0 guard; 7 signed switch targets; caller overwrites')
```
