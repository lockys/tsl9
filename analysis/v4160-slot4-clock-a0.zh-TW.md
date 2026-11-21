# 槽 4 的兩個間接呼叫共用一個時鐘指標

沿 `0x58c52` 首次進入、傳入 a0 尚未被碰觸的路徑。V1.31 參考程式的 `0x58dfe` 執行 `lw a5,564(s5)`，s5 在 `0x58c66` 設為 `0x20003000`，所以取的是設定首 word **`[0x20003234]`**，不是後來的副本 `[0x200031e0]`。到兩個 `jalr a5` 之間沒有重載 a5。

狀態 181 且 `[s4+1]` 的 bit 0 為 1 時，先讀無號 byte `[s0+60]` 到 a3，再清 `[s4+1]`。`0x58e06` 比較的是 a3 與 1：值為 0、1 走 `0x58e4a`，其餘 254 個值走 `0x58e0a`。兩處既不以 a0 選路，也不以它選指標。

原 APP `0x19bba..0x19bcc` 把 `0x191c6` 寫入傳入設定的首 word。若[參考設定複製](v4160-task-clock-postcopy.zh-TW.md)成功且此 word 未變，兩處就都進入 APP `0x191c6`。先前兩組周邊讀值若持續不一致，可停在輪詢而未碰 a0；若走到 `0x191f6: lhu a0,-2024(a1)`，則**首次碰觸是以 `0x40002818` 的新半字覆寫**。正常返回後，`0x58e10/0x58e50` 複製到 s1 的是時鐘結果，不是傳入的取消碼。若登記、設定內容或指標不同，不推定真正目標或其行為。

重現：依序傳入 decoded APP、V1.31 carrier。核對原始指令，解出設定首 word、間接目標來源、分支與首次取樣位址；不執行裝置，也不測週邊時序。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(f).read_bytes() for f in sys.argv[1:])
def ck(ok):
    if not ok:raise ValueError('slot4 clock evidence mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(buf,p,h):
    v=bytes.fromhex(h);ck(buf[p:p+len(v)]==v)
def w(buf,p):return int.from_bytes(buf[p:p+4],'little')
def imm(x):return (x>>20^2048)-2048
raw(a,0x11bba,'97f7ffff9387c7603ec0b7070400fc5b0a858297');ck((0x19bba+(w(a,0x11bba)&0xfffff000)+imm(w(a,0x11bbe)))&0xffffffff==0x191c6)
raw(b,0x3f8c,'3735002041461305452397c0fb1fe780c039');raw(b,0x18c66,'b73a0020');raw(b,0x18de4,'1307500be39ae7f283471a00858b8dd78346c403a3000a00054783a74a2303dd89006372d7048297');raw(b,0x18e4a,'829737460f00aa84');raw(b,0x18e0c,'37460f00aa84')
dst=(w(b,0x3f8c)&0xfffff000)+imm(w(b,0x3f92));ck(dst==(w(b,0x18c66)&0xfffff000)+imm(w(b,0x18dfe))==0x20003234)
x=w(b,0x18e06);d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1;ck((x>>12&7,x>>15&31,x>>20&31)==(7,14,13));ck(0x58e06+d==0x58e4a and sum(1>=v for v in range(256))==2)
raw(a,0x111c6,'37360040835686810357868142074183e31ad7fe373600408356c6818357c681c207c183e39ad7feb735004003d6858103d58581');x=w(a,0x111f6);ck((x&127,x>>12&7,x>>7&31,x>>15&31)==(3,5,10,11));ck((w(a,0x111ee)&0xfffff000)+imm(x)==0x40002818)
print('PASS: both calls via cfg[0]; 2/254 branch split; nominal APP first a0 touch is LHU at 0x191f6')
```
