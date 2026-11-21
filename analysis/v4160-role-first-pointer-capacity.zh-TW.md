# `0x20003410` 的一個非零寫入來源：先檢查容量

接續[外層登記條件](v4160-first-role-nested-registration.zh-TW.md)。V1.31 參考映像的 `0x5397c` 不是無條件配置。令 `B=0x200033b8`：

* `0x5398e/92` 讀兩個無號 byte，只有 `B[62] < B[63]` 才去配置；否則返回零。`B[63]=0` 時，無論第一個 byte 是多少，此函式都到不了目標寫入。啟動清零若完成，兩個 byte 與指標 word 都在清零範圍。
* 通過比較後，以 `a0=192,a1=577` 呼叫候選配置函式；返回零仍退出。正常返回、清零函式保持 s0/s1 等前提下，`0x539da` 測的是 **`B+92`**，而非目標 `B+88`。若 `B+92` 為零，`0x539de/e0/e2` 依序把同一個非零配置結果寫到 `0x20003410/3414/3418`。因此在舊目標為零時能使其變成非零；不宣稱這是唯一或實機第一次寫入。
* 找到一個令容量非零的來源：在 `0x5362e` 初始化路徑上，`0x53670` 形成 `s0=B`，`0x5370a/0c` 寫 `B[63]=1`（依所經呼叫保存暫存器）。但從 `0x55bde` 讀完條件才由 `0x55bf8` 呼叫初始化的這一次，不能解釋**該次讀取前**容量已非零。若另有先前初始化、其他容量寫入或別的指標寫入，結論可能不同。

重現：以 V1.31 carrier 為參數。解碼比較及壓縮 store 欄位，窮舉兩個 byte；不執行裝置或配置函式。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes(); base=0x40000
def ck(v):
    if not v:raise ValueError('first pointer capacity evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
def w(p):return int.from_bytes(b[p-base:p-base+4],'little')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x53980,'b7340020');raw(0x5398a,'9387843b03c7e70383c7f703636af70001442285');x=w(0x53996);ck(x&0x707f==0x6063 and (x>>15&31,x>>20&31)==(14,15) and 0x53996+((x>>8&15)<<1)==0x539aa)
raw(0x539ac,'930510241305000c97c0fa1fe780c0682a8471dd');raw(0x539c6,'9384843b');raw(0x539da,'fc4ca1eba0cce0cca0d0');B=0x200033b8
for i in range(3):
    h=w(0x539de+2*i)&65535;off=(h>>10&7)<<3|(h>>6&1)<<2|(h>>5&1)<<6;ck(h&0xe003==0xc000 and (h>>7&7,h>>2&7)==(1,0) and B+off==0x20003410+4*i)
raw(0x53632,'b7340020');raw(0x53670,'1384843b');raw(0x5370a,'8547a30ff402');x=w(0x55bf8);v=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1;ck(x&4095==239 and 0x55bf8+(v^0x100000)-0x100000==0x5362e)
counts=[sum(n<c for n in range(256)) for c in range(256)];ck(counts==list(range(256)) and sum(counts)==32640);print('PASS: 65536 count/capacity pairs; zero capacity admits none; three pointer destinations')
```
