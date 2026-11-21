# 容量 byte 的整字與區塊初始化

對 V1.31 參考映像，以 `0x200033f7` 為目標，比對啟動和首次角色判斷的相對順序。`0x55bde` 是函式入口；真正的首次條件讀取是 `0x55be2`，讀的是 **`0x2000319f`**，不是容量。

|寫入|是否覆蓋容量|能否解釋首次條件讀取前的非零容量？|
|---|---|---|
|啟動清零迴圈，來源 `0x402a8`|是。從 `0x20002ef8` 起的第 319 號 word（從 0 起算）覆蓋 `0x200033f4..f7`，容量是最後一個 byte。|不能。正常完成後寫入的是零。|
|`0x53650` 呼叫 296-byte fill|是。`[0x200033b8,0x200034e0)` 的第 63 號 byte。|經 `0x55bf8` 進入的這一次不能：先讀 `0x55be2`，非零則跳過，零才走到呼叫；且 fill 參數也是零。其後設定容量為 1 是另一條指令。|
|`0x5eb64`、`0x5f864` 的半字與 `0x5e6ac` 的整字|目的依 `s0` 而定，非固定命中。|這三處的來源暫存器都是 `x0`，即使覆蓋也不能產生非零。|
|`0x5e700` 的整字|寫 `s0` 到 `s4+60`，不是寫固定全域。|仍需核對物件及時序。若為四 byte 對齊之正常 store，要覆蓋容量，`s4` 必須是 `0x200033b8`；此時容量收到 `s0` 的最高 byte。|

最後一項在 `0x5e5c4` 函式內：入口讀 `[0x200033b8+204]`（即 `0x20003484`）為初始節點，`s4` 初值為零；`0x5e6d6/d8` 保存舊節點至 `s4`，再讀其 `+60` 繼續走訪。新增節點若有前驅，才走 `0x5e700`。若串列的所有前驅皆為正常 arena 節點（先前條件分析的 payload 下界 `0x200043b4`），則前驅不是 `0x200033b8`。這是條件排除，不是所有串列內容或啟動可達性的證明。

重現（參數是 V1.31 carrier；核對指定機碼與涵蓋範圍，不執行設備）：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('capacity init evidence mismatch')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x40292,'b737002037370020938787ef130747616373f700828023a007009107d5bf');raw(0x55bde,'b737002083c7f719411106c689eb373505001305c552efe0ae85efd07fa3');raw(0x53632,'b7340020b737002013068012814522c42a841385843b06c623a2074e4ac097d0fa1fe780c0d4')
raw(0x5e5c8,'373900209307893b22cc03a4c70c');raw(0x5e5e2,'014a');raw(0x5e6d6,'228a405c11bf');raw(0x5e6a4,'631e0a042326890c232e0402');raw(0x5e700,'232e8a0265b7');raw(0x5eb64,'231f0402');raw(0x5f864,'231f0402')
t=0x200033f7;start=0x20003000-264;last=0x20003000+1556;hits=[(i,p,t-p) for i,p in enumerate(range(start,last+1,4)) if p<=t<p+4];ck(hits==[(319,0x200033f4,3)]);base=0x20003000+952;ck(t-base==63 and 63<296 and base+204==0x20003484 and (t&~3)-60==base<0x200043b4);print('PASS: startup word 319 byte 3; fill byte 63; conditional predecessor address')
```
