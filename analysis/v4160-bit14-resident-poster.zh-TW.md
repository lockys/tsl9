# 從設位端找到不依賴舊事件的 0x4000 來源候選

接續 [APP 續排與首次設位的區別](v4160-task3-bit14-origin.zh-TW.md)。本次反查 V1.31 參考設位函式 `0x4354a`（表槽 `0x40050`），不以 APP 中的遮罩常數為起點。

* **獨立投遞路徑 `0x4570a`。** 基址 `B=0x20003248`；先經 `[B+20]` 取指標、讀其 word、加一後寫回，再讀 `U8[B+3]` 為目的 ID。若是 255 就直接返回；否則 `0x45724..26` 準備 `a1=0x4000` 並尾跳 `0x4354a`。此路徑不讀舊事件作為投遞條件，也不經計時器配置。若增量操作成功、當次 `U8[0x2000324b]=3`、設位時登記數大於 3 且事件表有效，就能向 task 3 投遞該位，包括原位為零時。**這是可以解釋首次設位的程式路徑，不是已確認的首次發送者。**
* **目的 ID 不是常數 3。** `0x46586..0x46594` 的另一段程式在同一基址 +2 寫入半字 `0xff00`，按小端序會令 +3 成為 255。此處只識別一個寫入來源，沒有證明其先後，更沒有證明執行 `0x4570a` 時 +3 已被設定為 3。
* **反查也找到動態遮罩。** `0x568d0` 和 `0x6a6c6` 兩個直接跳轉/呼叫點均將 `1 << (byte & 31)` 截成半字；即使結果為 `0x4000`，該直線路徑明確傳 `a0=0`，不是 task 3。未窮盡間接呼叫與其他入口。上述壓縮 byte/halfword 指令按候選 Xwchc 解碼，非設備 ROM 身分證明。

離線檢查（參數：V1.31 carrier），從指令欄位還原讀寫偏移與三個直接目的地：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('resident bit14 poster mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def u(p,n): return int.from_bytes(raw(p,n),'little')
def fields(p,byte):
    h=u(p,2); off=2*(h>>5&3)+8*(h>>10&(3 if byte else 7))+((h>>12&1) if byte else 0)
    return h&3,h>>13,8+(h>>7&7),8+(h>>2&7),off
ck(u(0x40050,4)==0x4354a and fields(0x4571a,True)==(0,1,15,10,3) and fields(0x46592,False)==(2,5,15,14,2))
ck(raw(0x4570a,16).hex()=='b737002093878724d44b9842050798c2' and raw(0x4571c,10).hex()=='9307f00f6305f5009165')
ck(raw(0x46586,12).hex()=='b737002093878724130700f0')
for p,rd in [(0x45726,0),(0x568d0,0),(0x6a6c6,1)]:
    x=u(p,4); d=(x>>31<<20)|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1
    ck(x&127==111 and (x>>7&31)==rd and p+(d^1048576)-1048576==0x4354a)
ck(raw(0x568c4,12).hex()=='b395f500c205c18101450561' and raw(0x6a6ba,12).hex()=='85450145b395f500c205c181')
ck([n for n in range(256) if (1<<(n&31))&65535==16384]==list(range(14,256,32)))
print('PASS: independent bit14 post; destination byte +3; sentinel writer; two ID-zero shift sites')
```
