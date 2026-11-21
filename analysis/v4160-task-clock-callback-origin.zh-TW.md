# 首次排程前的兩個校準入口

[task ID 重讀](v4160-first-task-reload.zh-TW.md)之前的 APP 呼叫和參考 ROM 的可選回呼，原來指向同一個函式。這裡的兩個設定結構不同：早先 APP `0x199e2` 構造 **64 bytes** 的初始化設定；晚些 `0x19bcc` 傳入的是 **16 bytes** 的時鐘設定。

- 在前一結構，`0x19aa4` 的 PC 加上 `-748` 得 `0x197b8`；`0x19ab2` 保存到 `sp+64`，相對設定起點 `sp+16` 是 **+48**。若[早期設定複製](v4160-allocator-failure-slot-origin.zh-TW.md)正常完成，對應 `0x200031ec+48 = 0x2000321c`。這不是相鄰的失敗回呼 +52。
- APP `0x19ba8` 先直接呼叫 `0x197b8`。到 `0x19bcc`，若 `[0x40074]` 仍是參考 `0x43f46`，該函式從上述 **早期** `+48` 讀取回呼；非零時先於 `0x43f60` 間接呼叫，再重載傳入的時鐘設定指標。若槽值未改，這是第二次進 `0x197b8`，不是第二個未知函式。兩個入口都由 wrapper 設 a0=3 後尾跳 `0x1929a`。
- 校準函式先保存 caller s0，再把 `[gp+108]` 的 word 讀入 s0。核對整個 `0x1929a..0x196c4` 的反組譯：這個值用於有號除法等數值運算，**沒有以 s0 作為 load/store 的基址**。先前將它描述成已知指標並不準確。在 `0x19688` 從相同 frame 位置恢復 s0，最後還有向 `0x40022036` 的 halfword store 才返回。六個直接呼叫點均進只讀時鐘的 `0x191c6`。這不保證外設等待會結束，也不單憑保存/還原指令證明 stack 內容未變。

重現：以 decoded APP、V1.31 carrier 為參數。以下固定關鍵指令與兩條入口；是否安裝此 ROM、回呼槽是否保持、整份寫入集合是否排除 task byte，尚非本項證明。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(f).read_bytes() for f in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('clock callback origin mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def app(p,n): return a[p-0x8000:p-0x8000+n]
def jal(p,rd):
    v=int.from_bytes(app(p,4),'little'); ck(v&4095==rd*128+111)
    d=(v>>31<<20)|(v&0xff000)|((v>>20&1)<<11)|((v>>21&1023)<<1)
    return p+(d^0x100000)-0x100000
ck(app(0x19aa4,8).hex()=='97070000938747d1' and app(0x19ab2,2).hex()=='bec0')
t=0x19aa4+(int.from_bytes(app(0x19aa8,4),'little',signed=True)>>20)
ck(t==jal(0x19ba8,1)==0x197b8 and app(t,2).hex()=='0d45' and jal(t+2,0)==0x1929a)
ck(int.from_bytes(b[116:120],'little')==0x43f46 and b[0x3f46:0x3f64].hex()=='011122cc373400209307c41e9c5b06ceaa851304c41e81c72ac68297b245')
ck(0x20003000+492+(64-16)==0x2000321c)
ck(app(0x1929a,10).hex()=='5d719387c106a2c48043' and app(0x19688,2).hex()=='2644')
ck(all(jal(p,1)==0x191c6 for p in (0x19382,0x1938a,0x1949a,0x194a0,0x195d6,0x195dc)))
print('PASS: cfg+48 and direct call agree; wrapper sets 3; six clock-read calls')
```
