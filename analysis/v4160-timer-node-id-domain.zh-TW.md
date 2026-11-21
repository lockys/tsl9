# 兩個計時器建立入口會產生 ID 255 嗎？

在 V1.31 參考程式的兩個已知入口，正常完成的新節點都不是 255，但原因不同。判定的是節點首 byte，不是配置器 tag 的高 byte。

* `0x43728`：`43750` 讀任務數（unsigned byte），`43754` 在 `ID >= 任務數` 時跳到失敗出口。因此通過者最多是 254。`4378e` 保存通過檢查的 a0 到 s0；查找未命中、配置成功後，`43860` 按 Xwchc 把 s0 的低 byte 寫入節點 +0。這段推導需要中途算術、時鐘回呼、查找及配置正常返回且保持 s0；配置參數 `0xff00 | ID` 不是寫入節點的半字。
* `0x43414`：入口 a0 只在此路徑要求非零，**不是用它當任務 ID**。程式尋找索引 0..15 的空槽，用 tag `0xff00` 配置 16 bytes。空鏈與非空鏈的成功插入都走 `434c6: sb zero,0(a0)`，節點 ID 固定為 0，不依賴計數或輸入低 byte。`434f4` 的另一個 byte store 經可選輸出指標寫槽號，不是節點 ID 欄位；結論假設有效且不重疊的物件。

所以若鏈起初為空、只由這兩個入口建立節點、只觀察初始化完成後的鏈，且無其他寫入改變 ID 或鏈結，[前一報告](v4160-id255-service-results.zh-TW.md)的兩次 ID 255 查找都會未命中：`0x4022c` 回 1、`0x4005c` 回 6。後者仍有獨立的「目前任務」比較。這不是全域不可達證明：兩處都是先掛鏈再寫 ID，不能把完成後的性質套在中途觀測；沒有裝置 ROM 或所有寫者的證據。

重現：傳入 V1.31 carrier。比對控制流與寫入指令，解碼固定零值 store 及非空鏈跳回同一 store 的目的，枚舉所有 byte ID/任務數。非 CPU 模擬。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('node ID evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def val(p,n):return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
raw(0x43750,'83c7d7196378f500');raw(0x4378e,'2a84');raw(0x43820,'936504f0c205c1814145');raw(0x43860,'00a1');raw(0x4348a,'c165938505f04145');raw(0x434c2,'23a4a71e');raw(0x4350a,'48c7')
x=val(0x434c6,4);ck(x&127==35 and (x>>12&7,x>>15&31,x>>20&31,(x>>25<<5)|(x>>7&31))==(0,10,0,0))
x=val(0x4350c,2);d=sum((x>>i&1)<<j for i,j in zip(range(2,13),(5,1,2,3,7,6,10,8,9,4,11)));ck(x&0xe003==0xa001 and 0x4350c+(d^2048)-2048==0x434c6)
x=val(0x43754,4);ck((x&0x707f,x>>15&31,x>>20&31)==(0x7063,10,15));ids=set();ok=0
for count in range(256):
    for task in range(256):
        if task>=count:continue
        ids.add(task);ok+=1
ck(ids==set(range(255)) and ok==32640)
print('PASS: 65536 ID/count pairs; admitted IDs 0..254; second producer writes constant 0 on both insertion paths')
```
