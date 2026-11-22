# UUID 0x2902：註冊表與 TX 表的靜態連結

結論：依原 APP reset 初值，第四筆屬性的 `+12` 是 `0x20004080`，等於兩個 TX 查詢的 `gp+128`。不是屬性本身的地址 `0x20004030`，也不是 `+12` 欄位的地址 `0x2000403c`。

1. 原 APP reset 將 `0x1ab60` 起的 128 bytes 複製至 `gp=0x20004000`。`0x8fb8..0x8fce` 取 `[s0+304]`，傳入 `a0=gp, a1=4, a2=16, a3=0x19dfc`；當 s0 為 `0x40000` 時，這是服務槽 `0x40130`。16 是傳入的第三個參數；屬性列寬另由資料布局核對，不從該參數推定。回呼表 `0x19dfc+4` 是 `0x888c`。
2. 依 16-byte 屬性列解析，第四列來源 `0x1ab90`，四個 little-endian words 是 `2, 0x40018, 3, 0x20004080`。UUID 是經第二個 word **間接讀取**；兩份參考 resident 在 `0x40018` 都是 `02 29`。前兩筆參考 UUID 分別是 `0x2800,0x2803`；第三筆指回 APP 自訂 UUID，並非此 CCC 列。
3. 原 APP `0x888c` 的寫回呼在 UUID 比較相等的分支保留傳入的屬性指標，尾跳更新服務。配合[前一輪 V1.31 更新服務證據](v4160-ccc-update-reset.zh-TW.md)，若收到的是註冊的第四列，且欄位和 gp 保持不變，更新與 TX 查詢用的是同一張表。這不是裝機 ROM 身分、實際回呼參數、表內容或通知成功的證明。

離線複核（Python，依序傳原 APP、V1.31、另一份參考 carrier；不需連設備）：

```python
from hashlib import sha256
from pathlib import Path
from struct import unpack_from
import sys
a,r,s=(Path(p).read_bytes() for p in sys.argv[1:])
def need(ok):
    if not ok: raise ValueError('unexpected registration evidence')
need([sha256(x).hexdigest() for x in (a,r,s)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22','b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941'])
rows=[unpack_from('<4I',a,0x1ab60-0x8000+16*i) for i in range(4)]
need(rows[-1]==(2,0x40018,3,0x20004000+128))
for ref in (r,s):
    need([unpack_from('<H',ref,rows[i][1]-0x40000)[0] for i in (0,1,3)]==[0x2800,0x2803,0x2902])
need(a[0xfb8:0xfce].hex()=='8327041397160100938606e441469145138501008297')
need(unpack_from('<3I',a,0x19dfc-0x8000)==(0,0x888c,0))
for pc in (0x8a8a,0x8aae): need(a[pc-0x8000:pc-0x8000+4].hex()=='93850108')
print('PASS: 4 registered rows; UUID 0x2902 in both references; attr[3]+12 stores TX table address')
```
