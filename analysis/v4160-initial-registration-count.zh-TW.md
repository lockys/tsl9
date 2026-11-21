# 首三筆登記的起始索引從哪裡來？

`0x43c06` 並非讀取第一次配置的大小，而是讀 RAM byte `0x2000319d`。在 V1.31 參考初始化路徑上，`0x43b80` 先要求將 `[0x2000319c,0x200031c4)` 的 40 bytes 清零；計數就在第二個 byte。之後 `0x43bb4` 寫的是相鄰的**容量** `0x2000319e`，不是計數。在 Xwchc 解讀下這是一筆 byte store，不會跨到前一個 byte。

沿用[配置](v4160-second-allocation-frontier.zh-TW.md)、[回呼堆疊](v4160-cfg60-init-stack.zh-TW.md)與[釋放](v4160-second-release-table.zh-TW.md)的正常條件：heap 寫入在 arena；兩次配置與釋放的記帳半字在 `0x200031a2`；配置結果、兩個表基址與暫存區指標均為其他 word。根據既有寫址分析，正常的填值、四個 byte 的讀回及三次 `cfg+60` 呼叫也不寫計數。在指定回呼、有效指標、分離的 stack、正常返回、無非同步寫入或穿插註冊下，`0x43c06` 才會重讀到零。這不是對所有未知呼叫或已安裝 ROM 的判斷。

因此，若第一塊維持上述名義位置，三個表項依序是 `0x200047f4 ← 0x432a4`、`0x200047f8 ← 0x43326`、`0x200047fc ← 0x43326`。計數在第二筆與第三筆之間由 0 改為 3，**不能把觀察到 3 當成第三筆一定已寫完**。本段只登記地址，不呼叫這些函式。

重現：以 V1.31 carrier 為參數。固定關鍵指令，從呼叫處取得清零範圍、從指令取得 handler 常數；遍歷容量輸入並檢查三槽均在表內。負對照在清零後改變計數，驗證結果確實取決於重新讀到的值。這是局部資料流模型，不是完整 CPU。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('registration evidence mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(i): return int.from_bytes(b[i:i+4],'little')
need(b[0x3b76:0x3b88].hex()=='1305c41913068002814597d0fb1fe780c081')
g=0x20003000+(word(0x3b76)>>20); length=word(0x3b7a)>>20
need((g,length)==(0x2000319c,40))
need([b[i:i+2].hex() for i in (0x3bb4,0x3c06,0x3c1a,0x3c30,0x3c3e,0x3c42)]==['28a0','1c30','10c3','10c3','18b0','90c3'])
a=(word(0x3c0c)&~4095)+(word(0x3c16)>>20); d=(word(0x3c26)&~4095)+(word(0x3c2c)>>20)
t=0x200047f4
for c in range(256):
    state=bytearray([0xa5]*length); state[:]=bytes(length)
    state[2]=14+3*((c>>2)+(c&3))
    for injected in (None,1,255):
        buf=state.copy()
        if injected is not None: buf[1]=injected
        n=buf[1]; addr=[t+4*((n+i)&255) for i in range(3)]
        trace=[(addr[0],a),(addr[1],d),(g+1,(n+3)&255),(addr[2],d)]
        expected=[(0x200047f4,0x432a4),(0x200047f8,0x43326),(0x2000319d,3),(0x200047fc,0x43326)]
        need((trace==expected)==(injected is None))
        if injected is None: need(all(t<=p and p+4<=t+4*buf[2] for p in addr))
print('PASS: 256 capacity inputs; slots 0/1/2; 512 intervening-count controls differ')
```
