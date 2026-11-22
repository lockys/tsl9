# 774 前的兩個角色：區分讀記錄與事件派送

原 APP 的前兩個角色入口若對應 V1.31 參考表，其尾段分別可進入 `0x6d572`、`0x6ae7c`。不是每次都走到讀取段；例如第二個角色在 `0x6aedc` 閘門非零時已離開。在兩者各自走到讀取段、子呼叫正常返回且保存所需暫存器時，看到相同的三次 `0x440c2(id,length,dst)` 請求：

|記錄 ID|length|dst|第一／第二角色的呼叫點|
|---|---:|---|---|
|2|16|`0x200035d4`|`0x6d636 / 0x6aeea`|
|3|16|`0x200035e4`|`0x6d642 / 0x6aefa`|
|4|4|`0x20002ff4`|`0x6d67a / 0x6af36`|

這些 ID **不是事件位元**。在有儲存基址、讀取回呼有效、取得區塊緩衝並到達 `0x44142` 的路徑上，`0x440c2` 依 ID 檢查長度。以當下區塊大小為 256 為例，三筆記錄開頭分別在區塊偏移 192、212、232；通過內容檢查後，從記錄開頭 +4 複製所請求的 bytes。這不是讀取成功或資料內容的證明。

若需從儲存媒體載入區塊，`0x44136` 或 `0x441c8` 的目標來自 config 副本 +56（`0x20003224`），**不是**派送器的 `[0x20000000]`。若[已追到的 APP 設定副本](v4160-residual-frontier-2026-10-21/rom-storage-callbacks/README.md)保持，該回呼是 `0x1979a`，轉交 byte copy；命中已快取的區塊則可略過這次回呼。這只排除把這兩處當成直接派送；不涵蓋未知配置器或其他子呼叫。兩角色另在 `0x6d5dc / 0x6af3c` 使用的 `0x4600e` 只是把 a0 的低 byte 存入 `0x200033ae` 後返回，亦不執行 handler。

重查：在 repo 根目錄，以 V1.31 主區路徑為參數。

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
r=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('role storage mismatch')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p in (0x6d636,0x6aeea,0x6d642,0x6aefa,0x6d67a,0x6af36,0x6d5dc,0x6af3c):
    t=0x4600e if p in (0x6d5dc,0x6af3c) else 0x440c2
    ck(edges(r[p-0x40000:p-0x40000+4],p,t)==[(hex(p),'JAL',1)])
for p,h in [(0x6d626,'1386445dc1450945'),(0x6aee2,'1386495dc1450945'),(0x6d63a,'1306445ec1450d45'),(0x6aef2,'1306495ec1450d45'),(0x6d672,'130649ff91451145'),(0x6af2a,'37360020130646ff91451145'),(0x4412c,'83a7890303a5890089818297'),(0x441be,'83a7890303a5890089818297'),(0x4600e,'b73700202387a73a8280'),(0x44154,'938505fcb3c5f5028a05'),(0x441dc,'938545fdf199b5bf'),(0x441f2,'a115f5b7'),(0x44170,'4a8526869105')]:
    b=bytes.fromhex(h);ck(r[p-0x40000:p-0x40000+len(b)]==b)
ck(edges(r[0x4176:0x417e],0x44176,0x20000332)==[('0x44176','AUIPC/JALR',1)])
print('PASS: 6 record-read calls, 2 setter calls, 2 config callback loads and copy target')
```
