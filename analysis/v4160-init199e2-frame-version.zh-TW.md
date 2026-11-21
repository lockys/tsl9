# 0x199e2 保存表基址：APP 配置區與版本比較

`0x8ea8` 呼叫初始化函式。沿既有條件路徑，其入口 SP 是 `0x2000ffc0`；函式扣 96，令新 SP 為 F=`0x2000ff60`。`0x199ea` 把**來時的** s0 存在 F+88（`0x2000ffb8`），之後才自行把 s0 設成 `0x40000`。正常出口 `0x19b06` 從同一位置取回 s0；這並不是無條件把常數 `0x40000` 傳給下一個函式。

* 首個間接呼叫 `0x19a04` 要求比較 21 bytes。候選槽 `0x4003c → 0x20000442` 對應 carrier `0x406b2`；以既有 RAM 映射、Xwchc byte-load 解讀，其比較不寫輸入或 stack，只暫時清除並還原外設 word `0x4002420c`。APP `0x1ab1c` 與參考槽 `0x40034 → 0x6e6a0` 都以 `CH32V20x_BLE_LIB_V1.3` 開頭。第 22 byte 實際不同（APP NUL、參考 `1`），但不在比較範圍。因此在這個候選下返回 1，不進 `0x19a08` 自迴圈；**通過的是前綴比對，不是版本或 ROM 身分認證**。
* 清零要求只涵蓋 `[F+16,F+80)`；14 筆直接配置 store、helper 六個輸出 byte 與 APP 六次複製均不到 F+88。名義 SP 下，清零末端為 `0x2000ffaf`，與保存 word 之間還有八個 byte。原 APP 的直接 gp/MMIO stores 也不以此保存 word 為目的。正常出口先讀 ra、s0，再寫兩個固定外設 word，沒有再寫 s0。
* **尚未封閉的呼叫：**`0x19aec` 把 `F+16` 指向的配置交給 `[0x400a4]`。APP 資料區不重疊，並不能證明被呼叫的 resident 及其回呼都不改保存字。非零返回在 `0x19af0` 停住；零返回才經 `0x19106` 到正常出口。這裡不作實機可達性結論。

重現：依序提供原 decoded APP、V1.31 carrier；另外以 APP 執行 `check_v4160_cfg12_writes.py` 重查配置 store 清單。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('init frame/version evidence mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def app(p,n): return a[p-0x8000:p-0x8000+n]
def u(x):return int.from_bytes(x,'little')
ck(app(0x199e8,34).hex()=='1d71a2cc23a0f118370404005c5c485886ce55469715000093850512829711e101a0');ck(app(0x19b04,18).hex()=='f640664423a2e710054723a4e71025618280');ck(app(0x19ae2,16).hex()=='b707040083a7470a0808829711c101a0')
p=0x199fc+(u(app(0x199fc,4))&0xfffff000)+(u(app(0x19a00,4))>>20);q=u(b[52:56]);ck((p,q,u(b[60:64]))==(0x1ab1c,0x6e6a0,0x20000442));x=app(p,22);y=b[q-0x40000:q-0x40000+22];ck(x[:21]==y[:21]==b'CH32V20x_BLE_LIB_V1.3' and (x[21],y[21])==(0,49));ck(b[0x6b2:0x6fa].hex()=='b747024003a7c72023a607200f10000001c599c1814711eab747024023a6e720054582808507e309f6fe3308f500b386f500034808009422e306d8feb747024023a6e72001458280')
s,l=u(app(0x199ea,2)),u(app(0x19b06,2));off=(s>>9&15)*4+(s>>7&3)*64;ck((s>>2&31)==(l>>7&31)==8 and off==((l>>4&7)*4+(l>>12&1)*32+(l>>2&3)*64)==88);F=0x2000ffc0-96;ck((F+16,F+80,F+off)==(0x2000ff70,0x2000ffb0,0x2000ffb8));print('PASS: same 21 bytes, different byte 22; config ends 8 bytes before the saved s0 word')
```
