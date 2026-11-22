# 同一 TX task 同時收到事件 1、2 時，哪個片段生效？

先區分已到期並設在 pending 半字的事件 2，和仍在 timer 中的請求。以下只分析前者；要求 handler、任務 ID 和 bank 綁定不變。

1. APP `0x8614` 若收到兩位皆設的遮罩，仍先測 `0x8000`、`8`。兩者皆無且 ID 匹配才在 `0x86b2` 選事件 1；本輪不會順便執行事件 2。兩條事件 1 出口都到 `0x873e` 返回 `mask XOR 1`，保留原來的 2。
2. 依 [V1.31 參考派送器](v4160-task3-dispatch-and-rearm.zh-TW.md)，交付時清 pending 槽，返回時合併 `live_pending | (returned & ~cancel_mask)`。例如交付 3，返回 2，期間又成功設 2，未取消時結果是 **2，不是兩次工作**。即使未另設 2，未取消的返回位也能留下。此處不保證下一輪即選到此 task，也不斷言舊 timer 已刪除。
3. 若同 bank 的新 TX 已寫總長並將游標歸零，且事件 1 正常完成片段準備，它以新描述元設定 `Q+2` 並把 `D[0]` 設為 10。後來事件 2 使用當時的 `Q+2` 請求配置；成功後再讀 `D+4`、`Q+2` 以 `D+6+游標` 為來源。因此在無其他改寫時，是**新 frame 的首段**，不是由舊事件保存的舊 frame。事件遮罩沒有片段版本或游標。
4. **準備失敗是另一條路。** `0x8758` 僅清 `D+2`，沒有同步清 `D[0]` 或 `Q+2`；事件 2 入口 `0x877a` 看的是 `D[0]`，不是 `D+2`。所以不能由「總長已清」推論已待處理的事件 2 一定被丟棄，也不能說它一定使用新算的長度。這是靜態欄位依賴，不是設備觀察。

重現：以原 APP BIN 為參數執行。位元枚舉是有限模型；參考派送器的指令核對見上方連結。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('TX simultaneous event mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
for p,h in [(0x8686,'93f78500'),(0x86b2,'93771400c5c7'),(0x873e,'134514002db7'),(0x8758,'23910400cdb7'),(0x875e,'93772400'),(0x877a,'83470b00f9c3'),(0x8796,'03d62400'),(0x87a8,'83554b0083a7cb0403d62400')]:
    ck(b[p-32768:p-32768+len(h)//2].hex()==h)
counts=[0,0,0]
for m in range(3,65536,4):
    g=0 if m&32768 else 1 if m&8 else 2; counts[g]+=1
    if g!=2: continue
    ret=m^1
    for live in (0,2):
        for cancel in (0,2): ck((live|(ret&~cancel))&2==(2 if live or not cancel else 0))
ck(counts==[8192,4096,4096]); print('PASS: 16384 simultaneous masks; 4096 select event 1; 16384 merge cases; live field loads checked')
```
