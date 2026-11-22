# 16-byte 列的末位：讀取、失敗修復與第一次統計

限 V1.31 參考映像與既定 RAM 複製映射；接續[初始化](v4160-row-init-fill-contract.zh-TW.md)。以下區分讀取服務的效果和呼叫者的動作。

* **命中並完成複製。** `0x6b2f6` 傳鍵 `512+6*i`、長度 16、目的 `P+16*i`。與 `0x7000+i` 的[重播鍵](v4160-record-replay-page-source.zh-TW.md)不同；非零設定基址的列鍵在 `0x4421e..0x44228` 算 `(key-512)/6=i` 作為頁索引。標頭命中時 `0x44292` 要求從標頭後四個位元組的位置複製 16 bytes；正常、非別名、完整複製時，列偏移 15 因而取標頭起點 +19 的 byte。服務回零，`0x6b2fa` 跳過修復。不是從回零本身推定所有路徑都寫了資料；基址為零的替代路徑不在此結論內。
* **服務回非零。** [呼叫者](v4160-replay-410-subcalls.zh-TW.md)兩次填六個 `ff`，再以半字清零偏移 12..13。若列指標穩定，偏移 **14、15** 都保留「服務返回時」的值，不保證等於呼叫前的值。不同於初始化，這裡沒有清偏移 14 的 byte store。
* **下一個統計 `0x6af88`。** 每列傳 `(P+16*i,255,6)` 到 `0x200004bc`；它比較前六個 byte，全部為 `ff` 回 1，第一個不符即回 0。呼叫者只在回零時累加。因此偏移 15 不參與這個判斷；不能外推至所有後續用途。

檢查方式：以 V1.31 參考 BIN 為參數。下列程式固定分支和載入的原始碼窗，解出統計子呼叫，並列舉 255 個可能索引與比較器的七種停止位置；不是設備測試。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('row read evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(o,h):
    s=bytes.fromhex(h); ck(b[o:o+len(s)]==s)
raw(0x421e,'930a05e0 1947 b3caea02'); raw(0x4288,'8505 8a05 2686 a295 4a85 97c0fb1f e780000a')
raw(0x2b2ee,'c145 2696 13050520 ef80dddc 1dc9'); raw(0x2b326,'83270900 be94 23960400 0504')
raw(0x2afb8,'83a7c9fb 13154400 1946 9305f00f 3e95 9750f91f e780404f 01e5 8504')
ck(0x6afc8+0x1ff95000+1268==0x200004bc)
raw(0x750,'0505 8346f5ff e397b6fe e31be5fe 37470240 2326f720 0545 8280'); raw(0x74c,'0145 8280')
for i in range(255): ck(((512+6*i)-512)//6==i and 511<512+6*i<0x7000)
for stop in range(7):
    for tail in range(256):
        row=bytearray([255]*16); row[15]=tail
        if stop<6: row[stop]=0
        reads=[]
        for j in range(6):
            reads.append(j)
            if row[j]!=255: break
        ck(reads==list(range(min(stop+1,6))) and (row[reads[-1]]==255)==(stop==6))
print('PASS: 255 page indices; 1792 prefix/last-byte cases; failure halfword ends at +13')
```
