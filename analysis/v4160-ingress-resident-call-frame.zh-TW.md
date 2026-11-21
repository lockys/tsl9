# 接收回呼的呼叫點與堆疊來源（V1.31 參考映像）

APP 初始化交出回呼表，不是執行回呼。本次沿候選常駐程式的寫入服務，對照原 APP 表與[快照框架](v4160-snapshot-caller-frames.zh-TW.md)：

* `0x4bb22` 建立 64-byte 框架。`0x4bb56` 呼叫 `0x4b650` 查表，傳回空指標則跳過回呼。非空時 `0x4bb5c` 讀表的第二個 word 到 a6；a6 為零也跳過。`0x4bb64..0x4bb6e` 整理參數，`0x4bb70` 才是 `jalr a6`，返回位置是 `0x4bb72`。若查到的是 APP 保持不變的 `0x19dfc`，目標才是 `0x888c`。
* 設 `E` 為常駐例程 `0x4bb22` 的入口 SP。若走上述路徑，先前子呼叫正常還原 SP、沒有切換堆疊，則 APP 入口 SP 是 `E−64`。若接著走到三種快照之一，256-byte 寫入區間為 `[E−592,E−336)`；不是以註冊點 SP 為基準。
* 參考映像主連續區段的半字對齊掃描，找到四個 `JAL ra,0x4bb22` 編碼：`0x4bc20`、`0x4bc92`、`0x4bcce`、`0x4be02`。它們是供下一步查各自上層框架的候選位置；編碼盤點不是可達性或完整呼叫者證明，未計間接或壓縮跳轉。

僅限指定版本、正常呼叫及相容 Xwchc 解碼。特別是 `0x4bb52` 的兩個 bytes 不應因標準解碼器顯示 invalid 就改以奇數位址接著反組譯。本次沒有量測 `E`、連線裝置或確認 resident 已安裝。

重現：Python 的第一、第二個參數分別是 decoded APP 與 V1.31 主連續區段 BIN。

```python
import hashlib,sys
from pathlib import Path
app,rom=[Path(p).read_bytes() for p in sys.argv[1:]]
def ck(v):
    if not v: raise ValueError('evidence mismatch')
ck(hashlib.sha256(app).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(hashlib.sha256(rom).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(app[0x19e00-0x8000:0x19e04-0x8000]==bytes.fromhex('8c880000'))
ck(rom[0xbb22:0xbb72].hex()=='397152d42e8a4ed69305e101aa89528522dc4ad856d206de26da328936c63ac4be8a9750fb1fe78040f0054435c1aa84a8873944eff0bfaf21cd03284500630908042247b246d6874a86a6854e850298')
def jal(pc,w):
    d=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1)
    return pc+((d^0x100000)-0x100000)
hits=[]
for i in range(0,len(rom)-3,2):
    w=int.from_bytes(rom[i:i+4],'little'); pc=i+0x40000
    if w&4095==0xef and jal(pc,w)==0x4bb22: hits.append(pc)
ck(hits==[0x4bc20,0x4bc92,0x4bcce,0x4be02])
ck(64+528==592 and 64+272==336 and 592-336==256)
print('PASS: APP field +4; 80-byte reference prefix; 4 JAL-ra candidates; 256-byte conditional snapshot')
```
