# 0x44056：四個 byte 寫到哪裡？

在[三欄皆非零](v4160-cfg-read-gate-44022.zh-TW.md)、APP 的 `0x1979a` 綁定未變，且沿用[名義入口堆疊](v4160-cfg60-init-stack.zh-TW.md)時，`0x44022` 扣 32 後的 SP 是 `0x2000ff20`。`0x44052` 取的是這個 SP+12，不是回呼再扣 16 後的 SP+12。APP 在 `0x2000ff1c` 保存自己的 ra，然後以 `(目的=0x2000ff2c,來源=0x08077c00,長度=4)` 呼叫槽 `0x4004c`。

V1.31 槽內容是 `0x20000332`。若 RAM 程式仍是參考副本，則它不是單一 word store：`0x20000358` 每次讀一個 byte，`0x20000362` 依序寫 `0x2000ff2c..0x2000ff2f`。此外入口和出口各寫一次外設 `0x4002420c`（先清零，後寫回先前讀值），沒有調整 SP 或再呼叫。讀取暫存 word 的結束位址（不含）與 APP 保存 s0 的 `0x2000ffb8` 相距 **136 bytes**；甚至與 `0x44022` 自己保存 s2 的 `0x2000ff30` 也是相鄰而不重疊。

正常返回後，`0x44058..0x4405c` 比較重讀的配置 +8 與這四個 byte 組成的 word；不檢查回呼的返回碼。這排除的是此指定路徑的直接 CPU 寫入，不證實機儲存內容、外設副作用或分支結果。

重現：先執行前述三欄與堆疊檢查，再以 V1.31 carrier 為參數檢查參考副本和位址；下列為寫址投影，不是完整 CPU 模擬。

```python
import sys,hashlib
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('read stack projection mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(int.from_bytes(b[76:80],'little')==0x20000332)
ck(b[0x5a2:0x5dc].hex()=='b747024003a7c72023a607200f10000001c599c1814711e6b747024023a6e7208280b386f50003c80600b306f500850723800601e317f6fec5b7')
sp=0x20010000-224; dst=sp+12; saved=0x2000ffb8
ck((dst,sp-16+12)==(0x2000ff2c,0x2000ff1c))
for sample in (0,0x08077c00,0xffffffff,0x12345678):
    raw=sample.to_bytes(4,'little'); mem={}; trace=[]
    for i in range(4):
        trace.append((0x08077c00+i,dst+i));mem[dst+i]=raw[i]
    ck(list(mem)==list(range(0x2000ff2c,0x2000ff30)))
    ck(int.from_bytes(bytes(mem.values()),'little')==sample)
ck(dst+4==sp+16 and saved-(dst+4)==136)
print('PASS: 4 byte destinations, 4 sample words, 136-byte gap')
```
