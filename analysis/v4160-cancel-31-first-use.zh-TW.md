# 取消回傳值：31 個有返回點的直接呼叫

範圍是原 APP 中 `jal ra,0x90b0` 的 31 個編碼。假設取消正常返回，追的是 a0 的**原值**；下游重新讀 RAM 不算使用原值。8 個 `jal x0` 尾跳另計。地址皆為 PC，非檔案 offset。

|返回後的去向|呼叫點|
|---|---|
|直線覆寫（15）|a1c4 a69a a6c8 aac0 b284 eec2 f098 fe30 fe54 feca ff2a 10738 13de0 17bd2 17c38|
|經跳轉、分支或下一個函式先覆寫（7）|a1d0 f4ca 14100 14190 143f8 1818e 181b2|
|本層正常出口原樣傳回（6）|9b12 ab38 fed6 ff36 1768e 17f72|
|依其他輸入可傳回或覆寫（2）|a1de a556|
|暫不歸類（1）|ad94：立即呼叫 a664，不能只看下一條 call 就宣稱原值失效。|

優先核對三個看似會測回傳碼的分支：

- `a1d0` 返回後跳到 `a0c4` 呼叫 `8440`。它以 `lbu a0,364(gp)` 覆寫 a0，`a0c8` 測的是 RAM byte。
- `143f8` 返回後從兩個 byte 組出比較值，再呼叫 `9334`。該函式第二條 `mv a0,sp` 已丟棄取消狀態；`14414` 比的是新呼叫的結果。
- `a556` 的分支 `a56a` 測 `((byte[gp+357]-1)&255)>3`。byte 為 1..4 時落到 `a57e` 覆寫 a0 並重新排程；其餘 252 個值走 `a59a` 還原並返回原值。不是「取消失敗才重排」。另一混合點 `a1de` 先測 `gp+175`，非零分支還受 stack 資料影響。

以下檢查分類清單與所有 JAL-ra 編碼一一對應，核對上述三例的關鍵指令並窮舉 byte 判斷。其餘列來自靜態逐點閱讀，不是全路徑模擬、實機執行或所有上層皆忽略結果的證明。

```python
import sys
from pathlib import Path
from hashlib import sha256
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('cancel inventory mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
s='a1c4 a69a a6c8 aac0 b284 eec2 f098 fe30 fe54 feca ff2a 10738 13de0 17bd2 17c38 a1d0 f4ca 14100 14190 143f8 1818e 181b2 9b12 ab38 fed6 ff36 1768e 17f72 a1de a556 ad94'; pcs=[int(z,16) for z in s.split()]; hits=[]
for i in range(0,len(b)-3,2):
    x=int.from_bytes(b[i:i+4],'little');d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    if x&4095==0xef and 32768+i+(d^1048576)-1048576==0x90b0:hits.append(32768+i)
ck(len(pcs)==31 and sorted(pcs)==hits)
for p,h in [(0xa1d4,'c5bd'),(0xa0c4,'efe0cfb763000512'),(0x8440,'03c5c1168280'),(0x14408,'ef40dff2330985401339190063158502'),(0x9334,'01110a85'),(0xa55a,'9387011683c757000d47fd1793f7f70f6368f702'),(0xa57e,'17050000'),(0xa59a,'b2402244924441018280')]:
    v=bytes.fromhex(h);ck(b[p-32768:p-32768+len(v)]==v)
ck([x for x in range(256) if ((x-1)&255)<=3]==[1,2,3,4]);print('PASS: 31 unique call sites; three branch audits; 256 gate values')
```
