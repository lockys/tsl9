# 初始化狀態決定 APP 是否重載 s0

`0x43d52` 恢復的是 resident 自己的 s0；**APP 原先在 `0x199ea` 保存的 s0，要到 `0x19b06` 才讀回**。兩次指令不可混為一談。

|V1.31 參考路徑|APP `0x19aee` 看到什麼？|
|---|---|
|入口檢查在建 frame 前退出|`0x43d5c/5e` 出口返回 2；APP 停在 `0x19af0` 自跳，不重載。|
|六個 byte 全為 `ff`；或配置 +8 非零而缺必要的 +56/+60|經 `0x43d50` 的共用出口分別返回 3、6；同樣不重載。|
|`0x43b3e` 正常返回到 `0x43d4e`|外層把狀態設為 0，**沒有傳遞內層結果**。APP 呼叫 `0x19106(64,1)`，所選分支只對 `0x40021014` 的 word 做 OR 64 並寫回，不寫堆疊。然後 `0x19b04` 取 ra，`0x19b06` 從當下 `SP+88` 重載 s0。|
|外部呼叫未返回，或未知回呼改了返回狀態、SP 或保存的 word|不能由靜態出口推出抵達重載，更不能推出重載值等於入口 s0。|

在既有名義 frame `SP=0x2000ff60` 下，存、取同為 `0x2000ffb8`。`0x19b08/0e` 的兩筆外設寫入在重載之後。先前[讀取回呼](v4160-cfg56-stack-read.zh-TW.md)與[不等分支](v4160-mismatch-saved-s0.zh-TW.md)排除了指定條件下的直接寫入，不是所有異步/未知 provider 保持該槽的證明。即使正常返回且狀態為零，也不能據此判定所有內部登記成功。

重現：原 APP、V1.31 carrier 為兩個參數。下列檢查從壓縮指令解出存取的暫存器和位移、分支位移；固定所選 leaf 完整指令窗。用原值與不同的模擬槽值作對照，驗證判斷是「重讀當下的值」，不是無條件回傳原值。這是出口模型，不執行未知回呼。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=[Path(p).read_bytes() for p in sys.argv[1:]]
def ck(x):
    if not x: raise ValueError('init reload evidence mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def h(pc):return int.from_bytes(a[pc-0x8000:pc-0x8000+2],'little')
s,l=h(0x199ea),h(0x19b06)
ck(s&0xe003==0xc002 and (s>>2&31)==8 and l&0xe003==0x4002 and (l>>7&31)==8)
save=4*(s>>9&15)+64*(s>>7&3); load=32*(l>>12&1)+4*(l>>4&7)+64*(l>>2&3)
ck(save==load==88 and 0x2000ff60+load==0x2000ffb8)
x=h(0x19aee);ck(x&0xe383==0xc101 and h(0x19af0)==0xa001)
d=(x>>12&1)*256+(x>>10&3)*8+(x>>5&3)*64+(x>>3&3)*2+(x>>2&1)*32
ck(0x19aee+(d^256)-256==0x19af2)
ck(a[0x11af2:0x11afc].hex()=='854513050004eff0efe0' and a[0x11106:0x11114].hex()=='99c5371702405c4b5d8d48cb8280')
ck(b[0x3d4c:0x3d62].hex()=='cd3b8147b240224492443e854101828089473e858280')
for status in (0,2,3,6,0xffffffff):
    for now in (0x40000,0x12345678):
        mem={0x2000ff60+save:now};pc=0x19aee+d if status==0 else 0x19af0
        got=mem[0x2000ff60+load] if pc==0x19af2 else None
        ck(got==(now if status==0 else None))
print('PASS: paired s0 slot +88; zero-only continuation; 10 status/slot cases')
```
