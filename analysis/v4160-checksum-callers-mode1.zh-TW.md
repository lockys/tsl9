# 同一校驗，不同的前置操作與成功處理

在 `0x14d2e` 的 mode 1 分支，`s0` 是這次入口收到的記錄指標 P；以 `[P+0]` 小端無號半字選擇路徑。兩處都把**各自這次的 P** 傳給 `0x1083c(0x1069e,P)`，不是說不同次呼叫指向同一實體記錄。假設各呼叫正常返回、保存 s0/棧；未追溯 P 的實機配置。

|記錄識別值|校驗前|校驗傳回非零後|
|---|---|---|
|820 (`0x334`)|到 `0x15182` 直接取 s0；`0x1518c` 呼叫共用判定包裝函式。|呼叫 `0x106e8`，不使用其返回碼，然後尾跳 `0xf860(P)`。|
|1001 (`0x3e9`)|到 `0x1522e` 先呼叫 `0x82a8(0,13,P)`，再取 s0；`0x15242` 呼叫同一包裝函式。|呼叫 `0xadd6(P)`，不使用其返回碼，然後尾跳 `0xfba2(P)`。|

第二路校驗前的操作值得區分：`0x82a8` 取槽 `0x4004c` 的服務，方向 0 使其參數為 `(0x2000c1b8+13*12,P,12)`，即目的候選 `0x2000c254`。它不是從第 13 列重新載入校驗指標，也不以複製服務的狀態決定是否校驗。不能用這段指令保證服務真的完成複製，或 P 的內容在呼叫過程中不變。

兩路判定為零均跳至 `0x14da2` 的共同返回序列；非零時包裝函式曾請求登記 `0x107c0`，但上表的成功分支看的是**校驗結果**，不是登記成功狀態。這只描述兩條已核對的 mode 1 路徑，非真機執行證據。

重播（repo 根目錄）：對固定 APP 逐條走兩個 ID 的比較分支，再解碼兩處失敗分支與後續呼叫/尾跳。用先前的 `analysis/check_v4160_callback_1083c.py` 交叉核對共用判定函式位址。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('checksum caller mismatch')
def w(p): return int.from_bytes(b[p-32768:p-32768+4],'little')
def sx(v,k): return (v^(1<<(k-1)))-(1<<(k-1))
def bd(v): return sx((v>>31<<12)|(v>>7&1)<<11|(v>>25&63)<<5|(v>>8&15)<<1,13)
def pin(p,h):
    v=bytes.fromhex(h);ck(b[p-32768:p-32768+len(v)]==v)
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
pin(0x14d34,'2a84');pin(0x14d48,'0a053a951c41ba978287');pin(0x14d5e,'83570400')
t=0x14d40+(w(0x14d40)&0xfffff000)+sx(w(0x14d44)>>20,12);ck(t+sx(w(t+4),32)==0x14d5e)
for ident,expected in [(820,0x15182),(1001,0x1522e)]:
    r={15:ident};p=0x14d62
    for _ in range(32):
        if p==expected: break
        v=w(p)
        if v&0xfffff==0x713: r[14]=sx(v>>20,12);p+=4;continue
        ck(v&127==99);x,y=r[v>>15&31],r[v>>20&31];taken={0:x==y,1:x!=y,6:x<y}[v>>12&7];p+=bd(v) if taken else 4
    ck(p==expected)
for p in (0x15190,0x15246): ck(w(p)&0x1fff07f==0x50063 and p+bd(w(p))==0x14da2)
for p,rd,target in [(0x1518c,1,0x1083c),(0x15242,1,0x1083c),(0x15234,1,0x82a8),(0x15194,1,0x106e8),(0x151a0,0,0xf860),(0x1524c,1,0xadd6),(0x15258,0,0xfba2)]:
    v=w(p);ck(v&4095==111+128*rd and p+sx((v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1,21)==target)
pin(0x1522e,'b54501452286');pin(0x15182,'a285');pin(0x15238,'a285');pin(0x15198,'22852244b2404101');pin(0x1524a,'2285');pin(0x15250,'22852244b2404101');pin(0x14da2,'b240224441018280')
ck(0x82b6+(w(0x82b6)&0xfffff000)+sx(w(0x82ba)>>20,12)+13*12==0x2000c254)
print('PASS: mode 1, IDs 820/1001, common reject, 7 JAL edges, separate success tails and slot 13 address')
```
