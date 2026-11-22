# 非零基址：同鍵更新失敗會復原舊鍵嗎？

不會，限於 V1.31 候選、Xwchc、寫入端命中同一快取頁，且原記錄空間不足、下一標頭未使用的路徑。這個結論指的是 **RAM 快取**，不是裝置上的頁面。

- `0x444c0..0x444c4` 比較下一偏移與當前偏移之差和請求長度。差值不足時跳到 `0x4450c`，將原標頭的鍵半字寫為 `0x00ff`，再依下一偏移繼續掃描。不是先確認能新增才改鍵。
- 未使用標頭走 `0x44516`。`0x44522` 是無號 `bgeu a1,a2,0x4438a`：若 `offset+len+4 >= (L-64) mod 2^32` 就返回 `10`。**相等也失敗**，不同於零基址路徑。返回段只還原寄存器，沒有復原舊鍵，也未呼叫寫回。
- 例如 `L=256`、原記錄佔 20 bytes（4-byte 標頭和 16-byte 資料）、新資料長度 64。若下一標頭偏移為 120，算得 188，小於 192，可以新增；若偏移為 124，剛好 192，不能新增。後一種情況下舊資料仍在快取，但其標頭已不再匹配原鍵。沒有證據表明實機上存在該頁面配置。

下列檢查從候選原碼解出分支欄位與目的位址，並核對 42 個對齊偏移的判定。它不是整個函式的執行器。後續是否持久化另見[快取寫回條件](v4160-replay-cache-flush.zh-TW.md)。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('backed-page evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def branch(p):
    w=int.from_bytes(raw(p,4),'little'); ck(w&127==99)
    d=(w>>31<<12)|((w>>7&1)<<11)|((w>>25&63)<<5)|((w>>8&15)<<1)
    return w>>12&7,w>>15&31,w>>20&31,p+(d^4096)-4096
ck(branch(0x444c4)==(4,13,9,0x4450c)); ck(branch(0x44522)==(7,11,12,0x4438a))
for p,h in [(0x444a2,'9305f00f'),(0x4450c,'0ea393160601c18249bf'),(0x44516,'5224b38596009105130606fc'),(0x4438a,'2945f2406244d2444249b249224a924a05618280')]: ck(raw(p,len(h)//2).hex()==h)
positions=range(24,189,4); rejected=[q for q in positions if q+64+4>=256-64]; ck(rejected==list(range(124,189,4)))
print('PASS: 2 branch targets; 42 offsets; last accepted 120, first rejected 124')
```
