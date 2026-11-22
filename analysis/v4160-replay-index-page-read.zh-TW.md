# 不同快取頁：讀頁回呼的寫入範圍

接續[同頁命中](v4160-replay-index-cache-hit.zh-TW.md)。限非零基址、有效快取指標、頁地址不符。V1.31 候選在 `0x444f8` **重新讀取** `L=U16[cfg+12]`（Xwchc），然後呼叫 `[cfg+56](s5,L>>2,B)`，其中 `B` 重新取自 `0x200031bc`。s5 是先前算好的頁地址；若設定有變，兩處頁長不必相同。

若回呼仍綁定原 APP `0x1979a`，它把 ra 存於入口 SP−4，並透過 `[0x4004c]` 要求從 s5 複製 `L & ~3` bytes 到 B。名義 L=256 是 256 bytes，不是 64 bytes；非四的倍數不補齊。依[候選複製服務](v4160-cfg56-stack-read.zh-TW.md)，正常非空複製依次寫 `[B,B+(L & ~3))`，另有兩次固定外設字寫入。回到 `0x44506` 後把 s5 寫至 `0x200031c0`，**不檢查回呼狀態**便回到標頭掃描。

若 B 是名義 arena 內仍有效且容量足夠的頁、範圍不回繞、堆疊與索引分離，且沒有外部副作用改 RAM，這次讀頁與地址更新都不會寫到較低的索引 `0x20002fba`。這只排除了讀頁步驟；不證讀到哪筆內容，也不涵蓋空指標時先執行的配置器。未連接設備。

重現：依序傳入原 APP BIN 和 V1.31 參考 BIN。下列是指令欄位與長度檢查，不是實機測試。

```python
import hashlib,sys
from pathlib import Path
a,b=(Path(x).read_bytes() for x in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('page read evidence mismatch')
ck(hashlib.sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
h=int.from_bytes(b[0x44f8:0x44fa],'little'); ck((h&0xe003,8+(h>>2&7),8+(h>>7&7),2*(h>>5&3)+8*(h>>10&7))==(0x2002,11,8,12))
ck(b[0x44fa:0x450c].hex()=='1c5c03260a0289815685829723225a0379b7')
ck(a[0x1179a:0x117b8].hex()=='b7070400fc474111328706c613962500aa853a858297b240014541018280')
ck(int.from_bytes(b[76:80],'little')==0x20000332)
rshift=int.from_bytes(b[0x4500:0x4502],'little')>>2&31
lshift=int.from_bytes(a[0x117a6:0x117aa],'little')>>20&31
ck((rshift,lshift)==(2,2))
for length in range(65536):
    n=(length>>rshift)<<lshift; ck(n==length-length%4 and n<=length)
ck(0x20002fba<0x200031c0<0x200043b4)
print('PASS: APP and candidate call windows; 65536 page lengths; 256 -> 256 bytes')
```
