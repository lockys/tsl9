# RAM 首筆記錄：何時能被讀回？

承接[零基址配置](v4160-zero-base-cache-lifecycle.zh-TW.md)。V1.31 參考程式在 `0x4454c` 重新載入 B，第一個標頭 H 在 B+4。**配置成功不代表此處是空標頭**：`0x44564` 按 Xwchc 讀 H[2]，只有不是 `0x5a` 才走以下新增分支。已經是 `0x5a` 時會比較既有鍵，不能套用首筆新增的結論。

* `0x445a6..0x445b8` 用重新讀取的 `U16[cfg+12] * U8[cfg+14]` 作容量 C。首筆偏移為 4；對長度 16 或 64，無號比較 `C < 8+len` 則返回 10，不執行標頭寫入；**等於**門檻即通過。這是程式的比較，不證實際配置大小。
* 通過後依序寫 H[2]=`0x5a`、LE16(H)=鍵的低 16 位、H[3]=下一個對齊偏移的低 byte，再要求 `0x20000332(B+8,src,len)`。服務在複製函式正常返回後設狀態 0，不檢查複製結果。因此標頭符合與資料完整是兩件事。
* 16-byte 列的門檻為 24、H[3]=24，資料在 `[B+8,B+24)`；64-byte 重播記錄則為 72、H[3]=72。B 和內容不變時，[讀取端](v4160-base-zero-row-read.zh-TW.md)可用相同的 16-bit 鍵命中；若來源、頁與讀取目的分離，兩次完整複製後才可推得讀回原資料。

限定零基址、首筆 marker 不符、記憶體有效的正常路徑；不是實機 ROM 或初始 RAM 內容的證明。離線核對（傳入 V1.31 carrier）：

```python
from pathlib import Path
import sys,hashlib
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('first-header mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,h in [(0x4550,'91461308a005'),(0x4564,'302363100605'),(0x45a6,'52246c24b385c502338696001106e3ebc5dcbdb7'),(0x4526,'13863400719a1106b296230107012310270134b379b7'),(0x44c8,'85078a072686ce853e9515b7'),(0x43f6,'97c0fb1fe780c0f30145')]: ck(b[p:p+len(h)//2].hex()==h)
w=int.from_bytes(b[0x45b4:0x45b8],'little'); d=(w>>31<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
ck(w&0x707f==0x6063 and (w>>15&31,w>>20&31)==(11,12) and 0x445b4+(d^4096)-4096==0x4438a)
for n in (16,64):
    ck(4+4+((n+3)&~3)==8+n)
    for c in (8+n-1,8+n,8+n+1): ck((c<8+n)==(c==8+n-1))
ck(0x443f6+0x1ffbc000-196==0x20000332)
print('PASS: six instruction windows; unsigned branch operands/target; 16/64-byte boundaries; copy target')
```
