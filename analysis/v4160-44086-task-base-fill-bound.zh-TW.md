# `0x44086` 填值：排除寫入任務表基址是否需要長度不變？

**不需要，但只限寫址分離。** 在 V1.31 參考的 `0x44022` 不相等分支，配置成功後 `a0` 仍是返回的目的 P。`0x4407e` 依 Xwchc 再讀無號半字長度至 `a2`；它不是直接沿用第一次配置的大小。`0x44086/8a` 呼叫 RAM `0x2000039c`。若 RAM 程式是參考啟動所複製的[填值迴圈](v4160-event4-fill-loop.zh-TW.md)，目的 byte 依序是 `[P,P+L)`，另對 `0x4002420c` 暫存／還原控制值，沒有 stack store。

若 P 在既有名義範圍 `0x200043b4..0x2000b183`，即使重讀的 L 取任一 `0..65535`，結束界最大為 `0x2001b182`（不含），不會 32-bit 回繞；起點已高於保存表基址的 `[0x200031c4,0x200031c8)`。所以不需假定 L 恆為 256 來排除**這次填值直接寫入這四個 bytes**。這不保證整次填值在配置物件內、存取成功、其他資料不變或之後的指標仍有效。

另一筆不能合併計算：`0x44090` 每輪從 `[s1+32]` 重讀指標至 a2，繼續分支在 `0x440bc` 用該值作 word store 的目的。這不是填值函式原先握有的 P；僅知 P 原在 arena 不足以排除後續 store。`cfg+60` 回呼與釋放函式的寫址亦須分開驗證。結論只針對參考映像，不代表裝置觀測。

重現（V1.31 主段作唯一參數；Xwchc 窄載入語義沿用[原指令表](v4160-44060-temp-buffer-stores.zh-TW.md)）：

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('task-base fill evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x4072:0x4086].hex()=='1387c41908d39384c41955dd52249305f00f0149')
u,j=[int.from_bytes(b[i:i+4],'little') for i in (0x4086,0x408a)]
ck(u&4095==0x97 and j&0xfffff==0x80e7 and 0x44086+(u&~4095)+((j>>20^2048)-2048)==0x2000039c)
ck(b[0x60c:0x63a].hex()=='374702408327c720232607200f10000001c53307c50011e6374702402326f72082800505a30fb5fee31de5fef5b7')
ck(b[0x4090:0x4096].hex()=='9050634df900' and b[0x40bc:0x40c2].hex()=='08c20297f9b7')
lo,hi=0x200043b4,0x2000b183
for n in range(65536):
    ck(0x200031c8<=lo<=lo+n<=hi+n<=0x2001b182<2**32)
ck(hi+65535==0x2001b182 and 0x4002420c>=0x200031c8)
print('PASS: 65536 fill lengths; upper endpoint 0x2001b182 exclusive; loop pointer load separate')
```
