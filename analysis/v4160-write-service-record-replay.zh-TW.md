# 第三處寫入服務呼叫：載入後逐筆重播

[第三處引用](v4160-write-service-upper-edges.zh-TW.md) `0x6c26e` 位於 V1.31 參考例程 `0x6c194`，不在先前的雙分支函式。入口扣 128 bytes，保存傳入 a2 到 s1；正常出口 `0x6c2f2` 加回 128。以下限候選 Xwchc 解碼、子呼叫正常返回並保持所需暫存器。

1. `0x6c1bc` 要求前次查找結果無號小於 RAM 容量 byte 才走這條路。`0x6c254` 呼叫 `0x440c2`，傳入 `(low16(0x7000+s0), 64, sp+32)`。非零返回直接跳到 `0x6c278`，略過整個重播。
2. 零返回時，`0x6af42` 逐筆處理 16 筆四位元組資料：反相前兩個 bytes 組成的小端 halfword，再反相 byte +2；byte +3 不變。因此原始半字 `0xffff` 轉為零，不呼叫；原始半字零反而轉成 `0xffff`，不是空項。
3. `0x6c266` 每次重新讀轉換後的半字，非零才從 `0x6c26e` 呼叫 `0x4bcbc(s1, halfword, byte_at_2)`。迴圈每次前進 4 bytes，到 `sp+96` 停。呼叫結果不參與迴圈判斷。若後續資料未被其他執行改動，呼叫次數等於原始半字非 `0xffff` 的筆數；不是固定 16 次。無實際資料頁或裝置執行證據。

重現：傳入 V1.31 主區段 BIN。先驗證讀取返回分支、兩個迴圈的原指令，再核對逐 byte 與整數反相的判定。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('record replay mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,h in [(0x6c194,'1971a6dab284'),(0x6c246,'1d65229542051010930500044181ef70fde605e10810efe07fce0010130901060e2089c530202685eff0fda41104e31989fe'),(0x6af42,'130705041e21110593c7f7ff231ef5fe8347e5ff93c7f7ff230ff5fee314e5fe8280'),(0x6c2f2,'09618280')]:
    raw=bytes.fromhex(h); ck(b[p-0x40000:p-0x40000+len(raw)]==raw)
for v in range(65536):
    lo,hi=v.to_bytes(2,'little'); decoded=(255-lo)|((255-hi)<<8)
    ck(decoded==(v^65535) and bool(decoded)==(v!=65535))
for mask in range(65536):
    rows=[(0 if mask>>i&1 else 65535) for i in range(16)]
    ck(sum(bool(v^65535) for v in rows)==mask.bit_count())
print('PASS: pinned loops; 65536 halfwords and 65536 record-presence masks')
```
