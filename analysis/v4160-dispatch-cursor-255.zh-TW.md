# 取消查找未命中時，是否仍會 OR 遮罩？

`0x2000319c` 不是「呼叫 handler 前設成 ID，返回時還原成 255」的欄位。在 V1.31 參考派送器，它是跨次使用的掃描索引。以下 `40xxx` 是複製前的 carrier 位址。

* 初始化的 40-byte 清零包含索引。`40b44..40b4e` 掃到空槽時先將索引加一並存回，再與登記數比較；結束掃描時 `40abc` 寫零。`40ab4..40ab8` 只有在索引小於登記數才選 handler，`40b5e` 重讀索引作第一參數。若其間未被改寫，進入 handler 時不可能是 255。
* Handler 正常返回後先依重讀的索引回寫 pending 半字，再於 `40b9a..40ba2` 重讀索引：**零保持零，非零才遞增**。`40ba6..40bac` 可能呼叫另一個回呼，之後 `40bb2..40bba` 重讀索引、登記數，若索引不小於登記數就跳回 `40abc` 清零。這不是還原先前值。若只假設登記數是 byte，登記數 255、handler 索引 254 時，中間回呼有可能看到 255；不能單靠 handler 入口檢查排除這一刻。
* 沿用正常容量公式 `14+3*((c>>2)+(c&3))`，全部 256 個設定 byte 的容量最大 **212**，名義 `c=14` 為 **29**。若登記數始終不超過這個容量、進入掃描時索引有效、無另外的索引寫入，掃描遞增與 handler 後遞增都至多暫達登記數，故連上述回呼前也不會寫出 255。

因此，在這些條件下，`0x4005c` 收到 ID 255 且查找未命中時，`439e6` 的不相等分支會略過 `439f4` 的遮罩寫入，仍回 **6**。未命中本身不是略過 OR 的理由；判準是執行比較當下的索引。沒有假設所有回呼皆無副作用，也未驗證設備 ROM。

重現：參數為 V1.31 carrier。鎖定讀寫及分支指令，對正常容量上界內每個非空登記數、每個合法起始索引檢查兩種遞增的中間值與最後索引；另保留超出容量前提的邊界對照。這是局部轉移模型。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('cursor mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p:p+len(v)]==v)
raw(0xab4,'8347c41963eec708230e0418');raw(0xb44,'850793f7f70f230ef418e3ecc7f48db7');raw(0xb5e,'0345c419');raw(0xb9a,'8347c41981c78507230ef418');raw(0xba6,'8327891c81c782972324091c0347c41983471a00e371f7f0');raw(0x39e2,'83c7c71963992701b737002003d7c71d598c239e871c')
def branch(p):
    x=int.from_bytes(b[p:p+4],'little');d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    ck(x&127==99);return x>>12&7,x>>15&31,x>>20&31,p+(d^4096)-4096
ck(branch(0xab8)==(6,15,12,0xb54) and branch(0xbba)==(7,14,15,0xabc) and branch(0x39e6)==(1,15,18,0x39f8))
caps=[14+3*((c>>2)+(c&3)) for c in range(256)];ck(max(caps)==212 and caps[14]==29)
def after(i):return (i+bool(i))&255
cases=0
for n in range(1,max(caps)+1):
    for i in range(n):
        for mid in ((i+1)&255,after(i)):
            ck(mid<=n and mid!=255 and (mid if mid<n else 0)<n);cases+=1
ck(after(0)==0 and after(254)==255 and cases==45156)
print('PASS: 45156 transitions; maximum capacity 212; count=255 control exposes transient 255')
```
