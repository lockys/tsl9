# 設定基址為零時，列的第 16 個 byte 從哪裡來？

承接[列讀取](v4160-row-read-byte15.zh-TW.md)。V1.31 參考映像中，`0x440e4` 遇 cfg+8 為零跳至 `0x442d4`。這條路徑不呼叫 cfg.read，也不以 `(key-512)/6` 選頁，而是取 `B = U32[0x200031bc]`。

- B 為零：返回 10，不複製。否則第一個標頭在 `B+4`。依 Xwchc，依序讀標頭 +2 的 marker、+0 的小端半字鍵。marker 不等於 `0x5a` 直接返回 10；只有 marker 正確但鍵不同時才讀 +3 的下一個偏移 `q`，下個標頭是 `B+(q & ~3)`，不是相對於當前標頭。
- 命中標頭 H：`0x44302` 呼叫 `0x20000332(dst,H+4,len)`，正常返回後 `0x44186` 設狀態零。對列呼叫者 len=16，若來源與目的有效、分離且完整複製，**dst[15] = H[19]**。不是以 cfg 基址零推論目的列清零。
- 無 B 或 marker 不符的兩個正常失敗出口都未呼叫複製；在獨立堆疊與無其他寫入的條件下，接續呼叫者的局部修復亦不寫偏移 15。未確定 B 的實際值、內容或實機使用此路徑。

離線重現（參數：V1.31 參考 BIN）。核對整個替代路徑、三個 Xwchc 載入的基址及偏移、複製目標和返回常數；以下 256 種偏移驗證地址算式，不代表 256 次實機讀取。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('base-zero read mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x42d4:0x4310]==bytes.fromhex('b7370020 83a5c71b 85dd 9147 9306a005 8983 13972700 2e97 3023 e313d6f2 1223 631c4601 8507 8a07 2686 be95 4a85 97c0fb1f e7800003 b5bd 3c33 d9bf'))
for o,kind,rd,d in [(0x42ec,0x2000,12,2),(0x42f2,0x2002,12,0),(0x430c,0x2000,15,3)]:
    h=int.from_bytes(b[o:o+2],'little'); ck(h&0xe003==kind and 8+(h>>7&7)==14 and 8+(h>>2&7)==rd)
    ck(2*(h>>5&3)+(8*(h>>10&3)+(h>>12&1) if kind==0x2000 else 8*(h>>10&7))==d)
ck(0x44302+0x1ffbc000+48==0x20000332 and b[0x4186:0x4188].hex()=='0145' and b[0x4214:0x4216].hex()=='2945')
for q in range(256): ck((((q>>2)+1)<<2)+15==(q&~3)+19)
print('PASS: RAM lookup window; 3 header loads; copy target; 2 statuses; 256 offset cases')
```
