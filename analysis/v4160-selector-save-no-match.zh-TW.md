# 0x12aa0：三次查表未命中時，保存的 selector 可以保持不變

承接[上游索引來源](v4160-setup-selector-upstream.zh-TW.md)。令 E 為 `0x12aa0` 的入口 SP。它從 E 減 32 後在 `sp+12` 保存 a0；`0x1070a` 返回後從同址 **E−20** 讀回。保護的是這個 word，不是 a0 暫存器。`0x1070a` 自己將 ra 放在 E−36；`0x90b0` 的三筆保存也都在 E−32 以下。

可閉合的一條路徑：`0x90b0` 先後查找 `0x1061c`、`0x9b36`、`0x107c0`。若 15 列的 `row+4` 起初均不含這三值，每次掃到表尾直接返回 1，既不改列也不呼叫列相關服務。全零不是必要條件。兩次填零分別寫 nominal `gp+300` 起的 3 bytes、`0x2000bfb8` 起的 12 bytes；`0x1061c` 本身另寫後一區首 byte。兩區都不在列資料 `[0x2000be08,0x2000bebc)` 內。參考 fill 還會暫存／恢復 `0x4002420c`；`0x9af0` 視旗標可能寫 `0x40010810`。這些都不是 selector 棧槽。

上述結論以 nominal gp=`0x20004000`、兩次槽 `0x40048` 均綁定[已核對的 V1.31 fill](v4160-event4-fill-loop.zh-TW.md)、正常 RAM/MMIO 存取、無外部干擾且棧與固定寫入區分離為條件。因第一次未命中沒有改表，其餘寫入也不碰表，第二及第三次不必重新假設表被清空。在此路徑，讀回的 selector 確為入口值；未證實機走此路徑。**若有列命中**，可能呼叫 `0x40068` 並尾跳 `0x4005c`，其寫入尚未納入此結論。

驗證片段（repo 根目錄執行）：核對 BIN、查找鍵、掃描及返回指令；以高位 RAM 內一組對齊入口 SP 驗算範圍分離。這是寫址與控制流核對，不是對整個 CPU 的模擬。

```python
from pathlib import Path
from hashlib import sha256
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('selector preservation mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def pin(p,h): ck(b[p-32768:p-32768+len(bytes.fromhex(h))]==bytes.fromhex(h))
def w(p): return int.from_bytes(b[p-32768:p-32764],'little')
def addr(p): return (p+(w(p)&0xfffff000)+(int.from_bytes(b[p-32764:p-32760],'little',signed=True)>>20))&0xffffffff
pin(0x12aa0,'01112ac606ceefd05fc63245');pin(0x1070a,'411106c6eff05f920145eff09ff0');pin(0x1003a,'0d4681451385c1120283');pin(0x1071c,'bc4731468145');pin(0x1061c,'97c7ff1f238e0798');pin(0x9af0,'83c7810a91e7b7170140094723a8e7808280')
keys=[addr(p) for p in (0x10624,0x10730,0x1073e)]; base=addr(0x90b2); dst=addr(0x10722)
ck(keys==[0x1061c,0x9b36,0x107c0] and base==0x2000be08 and dst==0x2000bfb8)
pin(0x90ba,'22c426c206c60144be843d47d4436394a604');pin(0x9110,'0504b107e319e4fab24022449244054541018280')
def apart(a,n,b,m): return a+n<=b or b+m<=a
fixed=[(0x2000412c,3),(dst,12),(0x4002420c,4),(0x40010810,4)]
ck(all(apart(base,180,p,n) for p,n in fixed)); count=0
for e in range(0x2000ca00,0x20010001,16):
    ck(all(apart(e-64,64,p,n) for p,n in fixed+[(base,180)]))
    ck(all(apart(e-20,4,e+off,4) for off in (-36,-60,-56,-52,-44,-40)))
    count+=1
print('PASS:',count,'aligned stack placements; 3 lookup keys; fixed stores separate from rows and stack')
```
