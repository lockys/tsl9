# 64-byte 記錄寫入返回 10：三個呼叫端會停嗎？

限 V1.31 參考映像，從三個已知 64-byte 寫入點正常返回開始分析；不假定裝置採用這版 ROM。**三處皆無依狀態 10 跳過 `0x44310` 的分支**，但對外回報不同：

|寫入點|寫回前如何處理 a0=10|正常寫回函式返回後|
|---|---|---|
|`0x6b120`|`0x6b12c` 將狀態 OR 入 s0；重新載入旗標，在 `0x6b136` 呼叫|返回七筆狀態 OR 的低 byte，保留 10 的置位位元，不一定恰為 10|
|`0x6b632`|`0x6b63e` 以列基址覆蓋 a0；按當前索引要求複製 16 bytes 至列，再寫 `[s0]=s5`；重新載入旗標，在 `0x6b65e` 呼叫|`0x6b662` 設 a0=0|
|`0x6b8dc`|`0x6b8e4` 直接以旗標覆蓋 a0，在 `0x6b8e8` 呼叫|跳到 `0x6b894` 設 a0=1，與記錄寫入狀態無關|

三處旗標均取自 `0x20002ef0`。**呼叫寫回函式不等於已經寫回。** 只有當時旗標恰為 1、設定基址、寫回回呼與快取指標皆非零，才會要求回呼寫出當前頁。若[改鍵失敗](v4160-backed-page-rekey.zh-TW.md)後頁指標、地址與內容仍保持，要求寫出的才是那張已改鍵的頁。第二條路徑還要前面的複製與寫入正常完成；不能把頁身分或實機持久化當成已證。詳見[寫回條件](v4160-replay-cache-flush.zh-TW.md)。

檢查：參數為 V1.31 參考 BIN。解出六個 JAL 和一對 AUIPC/JALR，固定三段續行指令及兩個結果常數；不執行回呼。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('caller evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def word(p): return int.from_bytes(raw(p,4),'little')
for p,t in [(0x6b120,0x4435c),(0x6b136,0x44310),(0x6b632,0x4435c),(0x6b65e,0x44310),(0x6b8dc,0x4435c),(0x6b8e8,0x44310)]:
    w=word(p); d=(w>>31<<20)|((w>>12&255)<<12)|((w>>20&1)<<11)|((w>>21&1023)<<1); ck(w&4095==239 and p+(d^1048576)-1048576==t)
p=0x6b64a; u,v=word(p),word(p+4); ck(u&4095==151 and v&0xfffff==0x80e7 and p+(u&0xfffff000)+((v>>20)^2048)-2048==0x20000332)
for p,h in [(0x6b124,'b73700201374f40f498c03c507ef1374f40f'),(0x6b636,'83470900373700200325c7fb92074146d2853e95'),(0x6b652,'23205401b737002003c507ef'),(0x6b662,'0145'),(0x6b8e0,'b737002003c507ef'),(0x6b8ec,'65b7'),(0x6b894,'0545f9b7')]: ck(raw(p,len(h)//2).hex()==h)
print('PASS: 3 write/flush call pairs, row copy target, 3 continuations')
```
