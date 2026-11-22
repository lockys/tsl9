# 設定重試：定時器成功與否，不改變這次 handler 的返回遮罩

接續[重試 ID](v4160-setup-retry-id.zh-TW.md)。在事件 1 分支，APP `0x16fb2` 請求 `(本次派發 ID, 1, 48)`。若槽正常返回且 s0 保持，不論服務返回 0 或 1，`0x16fb4` 都跳到 `0x16f9e`，將 a0 **覆寫**成 `入口遮罩 XOR 1`。此路徑要求最低位已設（mask 1）、mask 2/4 未設，因此效果是清除 mask 1 並保留其他位元。服務拒絕不會使 handler 以返回值保留這次重試事件；其他來源仍可能再送事件。

若槽是 V1.31 參考 `0x43728`，依[已核對的服務分支](v4160-first-schedule-request.zh-TW.md)：

|條件（依執行順序）|正常返回的結果|
|---|---|
|ID 不小於當前任務數、無時鐘回呼，或第一次換算超過上限|0，不查定時器串列|
|通過門檻且命中同一 `(ID, event=1)`|1，只改既有節點 +8 的期限，不要求新空間|
|未命中、16-byte 配置失敗|0；若錯誤回呼存在，須等它返回|
|未命中、配置成功|1，設為表頭或接在表尾，再填節點欄位|

代入本次延遲：`q=(係數×48+800)//1600`。對所有無號半字係數，`0≤q≤1966`，均低於名義上限 4264967295；這不保證 ID、時鐘或配置成功。係數前後兩次讀取可不同。若維持 16000，期限增量是 **480 計數**（非 48 毫秒的實測），名義 modulus 為 `0xffffffff`。不假設裝置採用該 ROM、回呼必返回或串列遍歷一定結束。

以下在 repo 根目錄以 Python 執行；固定輸入身分，解碼 APP 的跳轉與返回值指令，並抽查參考服務分支。不是完整 CPU 模擬。

```python
from pathlib import Path
from hashlib import sha256
def need(x):
    if not x: raise ValueError('retry timer evidence mismatch')
a=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
r=Path('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin').read_bytes()
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def jump(pc):
    h=int.from_bytes(a[pc-32768:pc-32766],'little'); need(h&0xe003==0xa001)
    v=sum(((h>>src)&1)<<dst for src,dst in zip((12,11,10,9,8,7,6,5,4,3,2),(11,4,9,8,10,6,7,3,2,1,5)))
    return pc+(v^2048)-2048
need(jump(0x16fb4)==0x16f9e and jump(0x16fa2)==0x16f28)
w=int.from_bytes(a[0xef9e:0xefa2],'little'); need((w&0x707f,w>>7&31,w>>15&31,w>>20)==(0x4013,10,8,1))
need(a[0xef0c:0xef0e].hex()=='2e84' and a[0xefaa:0xefb4].hex()=='13060003854526858297')
for off,s in [(0x37aa,'6370ab02'),(0x3810,'01c904c5'),(0x3828,'4145'),(0x3832,'11e9'),(0x3856,'2326050004c523115501'),(0x3870,'c8c7')]:
    need(r[off:off+len(bytes.fromhex(s))].hex()==s)
n=0
for mask in range(65536):
    if mask&7!=1: continue
    for status in (0,1):
        regs={8:mask,10:status}; regs[w>>7&31]=regs[w>>15&31]^(w>>20)
        need(regs[10]==mask&~1); n+=1
q=[(c*48+800)//1600 for c in range(65536)]
need((min(q),max(q),q[16000],n)==(0,1966,480,16384))
print('PASS: 16384 mask/status cases; 65536 scale values; nominal delta 480')
```
