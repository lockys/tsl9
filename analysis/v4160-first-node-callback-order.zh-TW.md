# 先讀條件，再安裝 0x6089a

接續[首次寫入串列頭](v4160-lookup-head-first-writer.zh-TW.md)。比較的是 V1.31 參考映像的一次同步呼叫，不假定裝置 ROM 相同。

`0x61b20` 先 `jal ra,0x55bde`；該函式讀 `0x2000319f`。正常返回到 `0x61b24` 後，六條指令才形成 `0x61000-1894 = 0x6089a` 並把它寫到 `0x20003000+952+184 = 0x20003470`。**這是安裝函式指標，不是呼叫它。** 槽位和串列頭 `0x20003454` 是不同 word；兩者都在啟動清零範圍。即使稍後有人從該槽呼叫 `0x6089a`、在 `0x608a6` 配置節點，這次安裝也不能解釋先前那次讀取前已有節點。這不排除先前另一處安裝或直接進入。

另一入口 `0x59e64` 確實有直接呼叫來源：掃描參考 carrier 每兩 bytes 的四-byte JAL-ra 編碼，命中 `0x584a4`、`0x5c8c6`。前者從 `0x58498` 的序言直落；後者從 `0x5c8c0` 直落時要求 `s3==13`。兩個呼叫返回後的下一條都是呼叫 `0x5784a`；這次查找在可能的配置**之後**，不能作為配置本身的前置條件。`0x58498` 又有 `0x5895e` 和 `0x58d18` 兩個直接呼叫編碼。這些是候選控制流邊，不表示它們在首次角色初始化前可達，也不是所有間接引用清單。

以 V1.31 carrier 為參數驗證：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes();base=0x40000
def ck(ok):
    if not ok:raise ValueError('node callback evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x61b24,'b7370020371706009387873b1307a78923ace70a');raw(0x55bde,'b737002083c7f719');raw(0x58498,'411106c626c222c44ac0aa84');raw(0x5c8c0,'b5476397f90e')
ck(0x61000-1894==0x6089a and 0x20003000+952+184==0x20003470)
edges={}
for i in range(0,len(b)-3,2):
    w=int.from_bytes(b[i:i+4],'little')
    if w&4095!=239:continue
    v=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1;p=base+i;edges[p]=p+(v^0x100000)-0x100000
ck([p for p,t in edges.items() if t==0x59e64]==[0x584a4,0x5c8c6]);ck([p for p,t in edges.items() if t==0x58498]==[0x5895e,0x58d18]);ck([edges[p] for p in (0x61b20,0x584a8,0x5c8ca,0x608a6)]==[0x55bde,0x5784a,0x5784a,0x57962]);print('PASS: post-read callback slot 0x20003470; 8 direct call edges')
```
