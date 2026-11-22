# 時鐘設定第四個 word：先清零，先讀一個 byte，再複製四個 byte

`0x19b56` 配置 32-byte frame，`0x19b60/62/64/66` 依序把 zero 存到 SP+0/+4/+8/+12。校準返回後只覆寫前三個 word。因此 SP+12 並非未初始化的 stack 資料。在前述[校準寫址](v4160-calibration-store-footprint.zh-TW.md)、名義 stack、正常呼叫返回且無其他改寫的條件下，`0x19bcc` 傳入的最後四個 byte 皆為 0。

V1.31 參考實作在可選回呼之後才檢查設定指標和欄位。採 WCH 壓縮指令解讀時，`0x43f70/74` 讀 a1+8/+10 的半字；`0x43f78` 則是從 a1+12 讀**一個無號 byte** 到 a5。若前面檢查已過且這個 byte 為零，`0x43f7a` 直接跳 `0x43f8c`；不讀另一設定 s0+21，也不走其組合值檢查。非零不表示必然拒絕。複製長度是 16，故成功時來源 +12..+15 都會被逐 byte 讀取，寫到 `[0x20003240,0x20003244)`。不是把第四個 word 整體當布林值判斷。例：小端 `0x01000000` 的低 byte 仍為零，但成功複製的第四個 byte 會是 1；這只是用來區分兩種解讀的對照值，不是 APP 預設。

重現：將兩個參數依序設為 decoded APP 與 V1.31 參考 carrier。核對欄位、分支與複製指令；複製器執行驗證見[16-byte 複製](v4160-task-clock-copy16.zh-TW.md)。不證裝置安裝此 resident、回呼不改記憶體或複製一定成功。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('fourth-word evidence mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for i in range(4):
    h=int.from_bytes(a[0x11b60+2*i:0x11b62+2*i],'little'); ck(h&0xe1ff==0xc002 and (h>>9&15)*4==4*i)
ck(b[0x3f78:0x3f7c].hex()=='dc2589cb')
h=int.from_bytes(b[0x3f78:0x3f7a],'little'); ck((h>>13,h&3,8+(h>>7&7),8+(h>>2&7),8*(h>>10&3)+2*(h>>5&3)+(h>>12&1))==(1,0,11,15,12))
h=int.from_bytes(b[0x3f7a:0x3f7c],'little'); ck(h&0xe003==0xc001 and (h>>7&7)==7)
d=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5); ck(0x43f7a+d==0x43f8c)
ck(b[0x3f8c:0x3f9e].hex()=='3735002041461305452397c0fb1fe780c039')
print('PASS: four zero stores; byte +12 zero branch to 0x43f8c; copy length 16')
```
