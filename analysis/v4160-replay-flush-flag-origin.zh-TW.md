# 重播頁寫回旗標：初值是 1，但可以改寫

在 V1.31 參考檔，啟動搬移的第 33 個 word 從 `0x6eb24` 複製到 `0x20002ef0`，小端 bytes 為 `01 05 02 01`。因此只要執行到這一次 store，旗標就是 1；此結論不需要假設尾端缺失的第 35 個來源 word 是零。後續清零從 `0x20002ef8` 開始，不含旗標。

另有兩處相鄰 `lui a5,0x20003; sb ...,−272(a5)`：

* `0x6ba8c` 寫入 s0 的低 byte。沿 `0x6b9a0` 設 s0=1 的直落路徑，中間兩次呼叫均指向 `0x2000039c`；若正常返回並保持 s0，此處再次寫 1。
* `0x6c82e` 寫入 a4。`0x6c3d6` 依 `(a0−1024)&0xffff` 分派；跳表 `0x6e74c` 的索引 24（參數低半字 `0x418`）指向 `0x6c822`。長度 a1 不等於 1 則返回 24 而不寫；等於 1 時，依 Xwchc 解讀從 a2 讀一個 byte，直接存入旗標，再返回 0。沒有布林正規化。相鄰索引 25（`0x419`）不是 setter：它直接呼叫 `0x44310(1)`，不從旗標取參數。

因此在[重播更新](v4160-replay-cache-flush.zh-TW.md)重新讀取時，只有先前最後一次有效寫入為 1 且無其他干擾，才滿足該項條件；設定為 2 與設定為 0 一樣不滿足。這不是對所有別名寫入的窮舉，也沒有證明 v4.1.60 APP 實際呼叫 setter 或設備安裝該 resident。

重現：於 repo 根目錄執行下段 Python。檢查兩段參考資料身分、搬移來源、直接 store、相鄰跳表項及分支片段；不執行回呼或硬體。

```python
from pathlib import Path
from hashlib import sha256
d = Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023')
b = next(d.glob('*00040000*bin')).read_bytes()
t = next(d.glob('*0006EAA4*bin')).read_bytes()
def ck(x):
    if not x: raise ValueError('reference mismatch')
ck(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(sha256(t).hexdigest() == '7416a8d7c1d595a759e14b05918b732a9168c6003af658359d8c3f452840b450')
ck(t[0x20002ef0-0x20002e70:][:4].hex() == '01050201')
def raw(pc, h):
    z = bytes.fromhex(h); ck(b[pc-0x40000:pc-0x40000+len(z)] == z)
raw(0x6b9a0,'0544'); raw(0x6ba88,'b7370020238887ee')
raw(0x6e74c+4*24,'22c8060034c80600')
raw(0x6c822,'8547e397f5be1822b73700202388e7eed5be0545ef70bdad')
raw(0x6c412,'614411a8'); raw(0x6c426,'01442285')
print('PASS: startup byte=1; parameter 0x418 stores byte; 0x419 requests flush')
```
