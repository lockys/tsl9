# 取消碼回到 0xcfe0 後，何時才會被覆寫？

`0xe66c` 是 `0xe220` 選擇分派函式內部的呼叫，不是上層入口。入口 `0xe234..0xe244` 保存 ra 到 sp+12、將 a0 移到 s0，最後跳過表；正常走到 `0xe736..0xe740` 才由該槽取回上層返回位址。原 APP 對 `0xe220` 有七處直接 JAL-ra（bc2c、bcda、c44c、cfdc、ec0e、ec46、ec9e）及兩處 JAL-x0（d55e、ec7e）；不含未知間接呼叫。

優先查 **0xcfdc**，因其輸入和前一輪的 64..66 有交集。`0xcf9c` 讀 byte、右移 5 位；令結果為 x。另兩處守衛要求舊 byte 與 x 各在 1..4（先前相等比較另有限制）。呼叫的 a0=x+62、a1=1、a2=0；故 256 個原 byte 中，64..159 的 96 個可提供 64、65、66。這是必要輸入篩選，不代表內部分支實際抵達取消點。

若該呼叫沿已分析取消路徑正常傳回 6，`0xcfe0..0xcfec` 處理另一個 RAM byte，不讀寫 a0；`0xcff0` 呼叫 `0x13c4e` 時仍帶 6。該函式依兩組資料測試（半字非 65534、旗標等於 1、另一 byte 非零），不比較 a0。兩組都不符合時由 `0x13cda` 直接返回；**首次覆寫為 `0xcff4: lbu a0,7(s0)`**。任一組符合時，走 `0x13c9e → 0x81b0`，後者亦不先改 a0，直到 `0x81ba` 間接呼叫 `[0x4007c]` 時仍傳入 6。此時首次使用取決於實際服務，不能把後面的乘法當成消費原取消碼。`0xec0e` 的返回點 `0xec12` 也直接呼叫同一 `0x81b0`。以上限正常讀寫與返回，未驗證實機。

重現：傳入原 decoded BIN。掃描半字對齊的 JAL 編碼，核對呼叫前後原碼與分支守衛的輸入範圍；不是實機 trace。

```python
import sys, hashlib
from pathlib import Path
b=Path(sys.argv[1]).read_bytes();base=0x8000
def ck(x):
    if not x:raise ValueError('upper caller evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667');hits=[]
for i in range(0,len(b)-3,2):
    x=int.from_bytes(b[i:i+4],'little');d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    if x&127==111 and base+i+(d^1048576)-1048576==0xe220:hits.append((base+i,x>>7&31))
ck(hits==[(0xbc2c,1),(0xbcda,1),(0xc44c,1),(0xcfdc,1),(0xd55e,0),(0xec0e,1),(0xec46,1),(0xec7e,0),(0xec9e,1)])
for p,h in [(0xe234,'411122c426c206c64ac0ba97ae842a848287'),(0xe736,'b24022449244024941018280'),(0xcf9c,'03455500'),(0xcfaa,'1581'),(0xcfc8,'9307f5ff93f7f70f6368f700014685451305e503ef104024'),(0xcfe0,'97f7ff1f938787f583c7c7002382f10eef60f04503457400'),(0x13c4e,'41679796ff1f83d666b479179797ff1f9387a7b3638ce60003c7570085466397e60003c747001377f70f0de383d6670041677917630cd70403c7970085466397e60483c7870093f7f70fa9c3411106c6ef402fd1'),(0x13cda,'8280'),(0xec12,'ef90efd9'),(0x81b0,'b7070400fc5f411106c68297')]:
    v=bytes.fromhex(h);ck(b[p-base:p-base+len(v)]==v)
ck([u for u in range(256) if ((u>>5)+62) in (64,65,66)]==list(range(64,160)));print('PASS: 7 direct calls, 2 tails; 96 candidate input bytes; return and provider prefixes pinned')
```
