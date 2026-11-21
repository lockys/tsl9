# 三個寫入服務入口的上一層引用

沿[已區分的三個入口](v4160-write-callback-outer-frames.zh-TW.md)查直接轉移與原值指標。V1.31 參考主區段各有一個匹配的 `jal ra`，三處均用 rasm2 在原位址另行解碼：

|呼叫位置|原始 bytes|目標入口|
|---|---|---|
|0x4d4b2|ef e0 4f f1|0x4bbc6|
|0x6c26e|ef f0 fd a4|0x4bcbc|
|0x4d484|ef e0 3f 94|0x4bdc6|

掃描範圍為原 APP、參考主區段及其候選 RAM 映射；每個半字位置檢查 JAL、標準 RV32C C.J/C.JAL、相鄰 AUIPC/JALR。另在每個 byte 位置查三個目標的 32-bit little-endian 原值，均未命中。這不能排除經位移、分段建址或執行期填入的函式表。兩個呼叫位置相距 46 bytes，但距離不證明共用入口。此為編碼盤點，不證可達、實機 ROM 或入口 SP。

從 repo 根目錄執行以下 Python，兩個參數為 decoded APP 和 V1.31 主區段檔案：

```python
import hashlib, sys
from pathlib import Path
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(ok):
    if not ok: raise ValueError('xref mismatch')
ck(hashlib.sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for base,data in [(0x8000,a),(0x40000,b),(0x20000000,b[0x270:0x2b0+2957*4])]:
    for dst,pc in [(0x4bbc6,0x4d4b2),(0x4bcbc,0x6c26e),(0x4bdc6,0x4d484)]:
        ck(edges(data,base,dst)==([(hex(pc),'JAL',1)] if base==0x40000 else []))
        ck(dst.to_bytes(4,'little') not in data)
print('PASS: three direct JAL-ra encodings; no literal target words across three views')
```
