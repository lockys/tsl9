# 零基址 RAM：舊鍵改寫後，讀取端走到哪一筆？

以正常的 16-byte 首筆更新成 64-byte 記錄為例，取鍵 `0x7000`，B 不變，第二個標頭原先沒有 `0x5a`。以下接合[既有鍵更新](v4160-zero-base-existing-key.zh-TW.md)、[新增標頭](v4160-zero-base-first-header.zh-TW.md)和[零基址讀取](v4160-base-zero-row-read.zh-TW.md)。

1. 第一個標頭在 B+4，下一偏移是 24。寫入端先將原鍵改為 `0x00ff`；原資料 `[B+8,B+24)`、標記與下一偏移均不因此清除。
2. 第二個標頭在 **B+24**，所需容量為 `24+4+64=92`。容量 91 時返回 10，第二標頭不建立，先前改鍵也沒有復原；容量 92 剛好足夠，寫入 `00 70 5a 5c`，並要求將 64 bytes 複製至 `[B+28,B+92)`。
3. 再讀 `0x7000` 時，第一個標頭仍有效但鍵不同，因此讀取端沿偏移 24 查第二筆。若新增失敗，第二筆標記不符就返回 10；若新增且完整複製，才從 B+28 讀回新資料。**舊資料仍在 RAM** 與 **能用原鍵讀回舊資料** 是不同結論。

驗證用一份共享 bytearray，不把寫入端的選擇傳給讀取端。假定 Xwchc、邏輯容量與有效配置一致、無其他寫入、來源目的分離；這是靜態指令加有限模型，不是實際裝置頁面。以 V1.31 carrier 路徑為參數：

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('replacement replay mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,s in [(0x4574,'b306d640e3d896f40ea393160601c182d9bf'),(0x45ae,'338696001106e3ebc5dcbdb7'),(0x4530,'230107012310270134b379b7'),(0x42ec,'3023e313d6f21223631c460185078a072686be954a85'),(0x430c,'3c33d9bf')]: ck(b[p:p+len(s)//2].hex()==s)
key=0x7000; old=bytes(range(16)); new=bytes(range(64,128))
def write(m):
    o=4; q=m[o+3]; ck(m[o+2]==90 and int.from_bytes(m[o:o+2],'little')==key and q-o<len(new))
    m[o:o+2]=(255).to_bytes(2,'little'); h=q&~3; ck(m[h+2]!=90)
    end=q+4+len(new)
    if len(m)<end: return 10
    m[h+2]=90; m[h:h+2]=key.to_bytes(2,'little'); m[h+3]=end; m[h+4:end]=new; return 0
def read(m,n):
    o=4; trace=[]
    for _ in range(2):
        h=o&~3; trace.append(h)
        if m[h+2]!=90: return 10,trace,None
        if int.from_bytes(m[h:h+2],'little')==key: return 0,trace,bytes(m[h+4:h+4+n])
        o=m[h+3]
    raise ValueError('outside two-record fixture')
for capacity in range(28,257):
    m=bytearray(capacity); m[4:8]=bytes.fromhex('00705a18'); m[8:24]=old
    ck(read(m,16)==(0,[4],old)); result=write(m)
    ck(len(m)==capacity and m[4:8].hex()=='ff005a18' and m[8:24]==old)
    ok=capacity>=92; ck(result==(0 if ok else 10))
    ck(m[24:28].hex()==('00705a5c' if ok else '00000000'))
    ck(read(m,64)==((0,[4,24],new) if ok else (10,[4,24],None)))
print('PASS: 229 capacities; initial hit; retained old payload; two-header readback')
```
