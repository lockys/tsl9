# `0x6b632` 返回後，哪一頁會被要求寫回？

限 V1.31 參考 ROM、候選 RAM 映射及子呼叫正常保持保存暫存器。從這次記錄寫入返回到下一次寫回呼叫，中間有兩筆不同的 RAM 更新：

1. 入口 `0x6b578/57a` 把兩個參數存為 s4、s5；`0x6b562/57c` 建立 s0=`0x20002fdc`。`0x6b5f8` 曾檢查索引小於當時列數，但 `0x6b624` 組鍵與 `0x6b636` 選列各自重讀 `0x20002fba`，不是同一次取樣。最後一次取樣後沒有重做界限比較。
2. `0x6b63e` 重讀 P=`[0x20002fbc]`。從 s4 複製 16 bytes 到 `P+16*i`；候選 `0x20000332` 以遞增順序讀寫，任一指標為零就跳過資料複製，仍有兩筆外設字寫入。隨後 `0x6b652` 將 s5 寫到 **固定字 `0x20002fdc`**，不是透過 s5 寫入。
3. 若 P 仍是有效列陣列、最後的 i 在配置內、列陣列和快取頁是兩塊不重疊的有效配置，且均在名義 arena、沒有回繞，則列寫入不碰快取頁，也不碰較低的快取指標和頁地址 `[0x200031bc,0x200031c4)`。固定字也不碰這兩欄、頁或旗標 `0x20002ef0`。在沒有非同步寫入或外設副作用改 RAM 的條件下，`0x6b65e` 所見的是 **`0x6b632` 返回時的同一頁、同一地址和內容**。單憑「兩塊都在 arena」只足以區分它們與低位址欄位，**不足以證明兩塊彼此不重疊**。

這是從返回點起的條件結論，不證明之前載入哪張頁、記錄成功、實際配置分離或儲存成功。是否發出寫回請求仍看[寫回條件](v4160-replay-cache-flush.zh-TW.md)。

重現：傳入 V1.31 參考 BIN；固定指令窗，解碼 SW 的兩個來源，核對 byte 索引/配置大小的全部有效組合（非硬體測試）。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('row/cache evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,h in [(0x6b562,'37340020'),(0x6b578,'2a8aae8a1304c4fd'),(0x6b5ec,'0345090083c717fc9384a4fbe376f5f8'),(0x6b624,'034509009d670a86930500043e95'),(0x6b636,'83470900373700200325c7fb92074146d2853e959750f91fe78080ce23205401'),(0x405c4,'b386f50003c80600b306f500850723800601e317f6fec5b7')]: ck(b[p-0x40000:p-0x40000+len(h)//2].hex()==h)
w=int.from_bytes(b[0x2b652:0x2b656],'little'); ck((w&127,w>>12&7,w>>15&31,w>>20&31,w>>25,w>>7&31)==(35,2,8,21,0,0))
slot=0x20003000-36; ck(slot==0x20002fdc and 0x20002ef0<slot and slot+4<=0x200031bc)
k=0
for n in range(256):
    for i in range(n):
        ck(16*i+16<=16*n and 0x200031c4<=0x200043b4+16*i); k+=1
ck(k==32640); print('PASS: fixed store and fresh index; 32640 in-allocation row intervals')
```
