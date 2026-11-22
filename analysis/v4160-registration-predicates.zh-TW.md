# 七條直接路徑：何時請求登記 0x107c0

令 `b[i]` 為從各路徑傳入之記錄指標起算的無號位元組。表列各路徑抵達 `0x1083c` **之後**的判定，不是進入各呼叫點的全部前置條件。假設記錄足夠長、可讀且在判定期間穩定，棧及呼叫正常；通過才執行 `0x820c(0)` 並請求 `0x9124(0x107c0,0,2000,0)`。不是實機事件或登記成功證據。

|32-bit JAL 位置|判定函式|回傳 1 的條件|
|---|---|---|
|108ea|1056e|`b[3]` 是 9 或 10，且 `b[4..8]` 五個位元組全零；不檢查 +9、+10。|
|10940（尾跳）|1059c|`b[3..10]` 全零。|
|10956|105c4|只看 `b[3] == 4`。|
|109d6|105d0|`b[7..10]` 全零；不要求 +3..6 為零。|
|10a28|105ec|`b[4] <= 14` 且 `b[5]` 是 `0x10,0x30,0x20,0xf4` 之一。|
|1518c、15242|1069e|`b[10]` 等於下面的模 256 加總。|

`0x1069e` 呼叫 `0xed00(record,7)`。種子是 `b[0]+b[1]` 的低 8 位；`b[2]` 是數量而非加數。對 `0 <= i < b[2]` 加入 `b[3+i]`，**跳過 i=7（也就是 +10）**。返回後才讀取 +10 作比較；即使數量小於 8 也會讀 +10。數量最大 255 時最後一個可能加數在 +257，不能假設 11-byte 記錄足夠，也沒有從此判定反推實際記錄長度。

重播：先執行同目錄 `check_v4160_callback_1083c.py` 驗呼叫點與 1059c。以下從 repo 根目錄執行，固定原 BIN 及所選指令；有限算術投影並不是獨立 CPU 模擬。

```python
from hashlib import sha256
from pathlib import Path
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def ck(x):
    if not x: raise ValueError('predicate mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for pc,h in [(0x1056e,'834735000547dd1793f7f70f636ff70003574500814701eb0357650009e78347850093b717003e8582808147edbf'),(0x105c4,'034535007115133515008280'),(0x105d0,'8347750091eb0357850009e78347a50093b717003e8582808147edbf'),(0x105ec,'03474500b94763e3e702834755004147054593f6f70d638ce600130700026388e7009387c7f013b51700828001458280'),(0x1069e,'41119d4522c406c62a84efe08fe58347a400b24022443385a7401335150041018280'),(0xed00,'035705000346250093578700ba9793f7f70f01479376f70f63e4c6003e8582806389d500b306e50083c63600b69793f7f70f0507c5b7')]:
    v=bytes.fromhex(h); ck(b[pc-32768:pc-32768+len(v)]==v)
for a in range(256):
    ck((((a-9)&255)<=1)==(a in (9,10)))
    for z in range(256):
        ck((a<=14 and ((z&223)==16 or z==32 or z-244==0))==(a<15 and z in (16,32,48,244)))
for n in range(256):
    r=bytearray((j*137+59)&255 for j in range(258)); r[2]=n
    half=int.from_bytes(r[:2],'little'); acc=(half+(half>>8))&255
    for i in range(n):
        if i!=7: acc=(acc+r[3+i])&255
    total=sum(r[:2])+sum(r[3:3+n])-(r[10] if n>7 else 0)
    ck(acc==total%256)
    for z in (acc,(acc+1)&255):
        r[10]=z; ck((z==(sum(r[:2])+sum(r[3:3+n])-(z if n>7 else 0))%256)==(z==acc))
print('PASS: six pinned code spans; 65536 field pairs; 256 lengths and 512 checksum comparisons')
```
