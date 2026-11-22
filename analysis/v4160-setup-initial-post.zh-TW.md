# 事件 1 的另一個來源是初始化，不是失敗後的補送

原 APP `0x9280` 直接呼叫 `0x17040`。此初始化函式登記 `0x16f00`，將返回 ID 的低 byte 存在 `gp+363`。若中途呼叫都返回，且 s1/s2 仍是表基址與該 byte 的地址，`0x171a4..0x171ac` **重新讀取**該 byte，以 `(live ID, 1)` 呼叫槽 `0x40050`。沒有第三個延遲參數的設定，也不是重試分支的 `0x40058`。初始化尾段不檢查登記結果是否為 255。

若採用 V1.31 參考槽 `0x40050 → 0x4354a` 與 Xwchc 解碼，ID 小於當前任務數時，向該 ID 的待處理半字 OR 入 1，返回 0；反之返回 3，不改待處理半字。原來已置位時不累計次數。這能解釋正常初始化後**第一次**設定事件從哪來；不能證明重試定時器遭拒後，初始化會再次執行或事件一定被派發。若 ID byte 已被改寫，目的地也未必是當初登記的列。

限定範圍：逐兩 bytes 掃原 BIN 的 32-bit JAL，目的地 `0x17040` 只見 `0x9280`；精確的 `LBU/ADDI ...,gp,363` 編碼只見 `0x1686c/0x17066`。`0x16858` 的局部表前三個半字是 **0、2、4**，不是 1；只對索引 0..2 如此判斷。以上不是所有間接路徑、指標別名或執行次數的普查。

驗證：在 repo 根目錄執行下列 Python。固定 APP/參考檔身分，核對初始化尾段、參考分支和局部表，並測試條件性 pending 更新；非完整 CPU 或裝置執行。

```python
from pathlib import Path
from hashlib import sha256
def ck(v):
    if not v: raise ValueError('initial post mismatch')
a=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(a[0xf1a4:0xf1ae].hex()=='bc480345090085458297' and r[80:84].hex()=='4a350400')
ck(a[0xe85a:0xe868].hex()=='b70702003ec4914718082316f100')
ck(r[0x355e:0x3566].hex()=='0347d7196370e502' and r[0x3574:0x358a].hex()=='1a21d98d0ea123a6d7200145828023a6d7200d458280')
hits=[]; gp=[]
for k in range(0,len(a)-3,2):
    w=int.from_bytes(a[k:k+4],'little'); pc=k+32768
    d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    if w&127==111 and pc+(d^1048576)-1048576==0x17040: hits.append((pc,w>>7&31))
    if w>>15&31==3 and w>>20==363 and w&0x707f in (0x4003,0x13): gp.append(pc)
ck(hits==[(0x9280,1)] and gp==[0x1686c,0x17066])
branch=int.from_bytes(r[0x3562:0x3566],'little'); ck((branch&0x707f,branch>>15&31,branch>>20&31)==(0x7063,10,14))
for old in range(65536): ck((old|1)==old+(1-(old&1)) and ((old|1)|1)==(old|1))
ck(sum(i<n for i in range(256) for n in range(256))==32640)
print('PASS: init JAL and GP sites; 65536 pending masks; 32640 admitted ID/count pairs')
```
