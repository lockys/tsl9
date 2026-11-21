# APP 是否直接設定重播寫回旗標？

V1.31 參考表 `0x40168` 的小端 word 是 `0x6c3d6`，即[參數分派入口](v4160-replay-flush-flag-origin.zh-TW.md)。以 v4.1.60 原 APP 在每個半字邊界掃描 `lw rd,360(rs)`：9 個編碼均可沿直落指令追到一次間接轉移。若基底是 `0x40000`，其目標取自該槽。逐一檢查轉移前最後一次設定 a0 的指令：

|load PC|轉移 PC|a0（參數號）|
|---|---|---|
|8f66|8f74|400|
|1259a / 125a8 / 125b6 / 125c6 / 125d6|125a6 / 125b4 / 125c4 / 125d4 / 125e4|40f / 408 / 409 / 40a / 40d|
|12782 / 12828|1278e / 12834|417 / 417|
|1332c|1333a（尾跳）|410|

表中數字均為十六進位。兩個 `0x417` 的長度是 7，不是 `0x418` 的單 byte 設定。這 9 處都不會以 `0x418` 或 `0x419` 進入分派；整個 APP 同一掃描範圍內也未找到以 `addi rd,x0,imm` 直接載入這兩個常數的編碼。這排除的是具體呼叫形式，不排除計算出的參數、轉交的函式指標、不同基底／位移或 resident 自行設定；不能由此認定重播時旗標必為 1。

重現（repo 根目錄，Python 3）：檢查輸入指紋、參考槽、完整命中集合、直接載入的參數與間接轉移暫存器。掃描含資料及長指令內部，不作執行可達性判定。

```python
from pathlib import Path
from hashlib import sha256
def ck(x):
    if not x: raise ValueError('evidence mismatch')
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
r=next(Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023').glob('*00040000*bin')).read_bytes()
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22' and r[0x168:0x16c].hex()=='d6c30600')
def val(p,n): return int.from_bytes(b[p-0x8000:p-0x8000+n],'little')
pcs=range(0x8000,0x8000+len(b)-3,2)
rows=[(0x8f66,0x8f70,0x400),(0x1259a,0x125a2,0x40f),(0x125a8,0x125b0,0x408),(0x125b6,0x125c0,0x409),(0x125c6,0x125d0,0x40a),(0x125d6,0x125e0,0x40d),(0x12782,0x1278a,0x417),(0x12828,0x12830,0x417),(0x1332c,0x13334,0x410)]
ck([p for p in pcs if val(p,4)&0xfff0707f==0x16802003]==[x[0] for x in rows])
for p,q,k in rows:
    ck(val(q,4)==(k<<20|0x513))
    rd=val(p,4)>>7&31
    if p==0x1332c: ck(rd==6 and val(q+4,4)==0x83020141)
    else: ck(rd==15 and val(q+4,2)==0x9782)
ck(not any((val(p,4)&0xfffff07f) in (0x41800013,0x41900013) for p in pcs))
print('PASS: 9 load/transfer sites; no 0x418 or 0x419 immediate selector')
```
