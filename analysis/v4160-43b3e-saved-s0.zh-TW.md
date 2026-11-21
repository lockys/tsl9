# 0x43b3e 初始化本體：與 APP 保存的 s0 比對

延續[呼叫端堆疊](v4160-cfg44-saved-s0.zh-TW.md)。V1.31 參考 ROM 的 `0x43d4c` 直接呼叫 `0x43b3e`。取入口 SP `0x2000ff50`，要保護的 APP word 起於 `0x2000ffb8`。以下區分寫入目的地和被寫入的指標值。

* `0x43b4e` 扣 16；ra、s0、s1 分別存到 `0x2000ff4c/48/44`。出口 `0x43c44..43c4c` 從相同位置重讀後才回收 frame。本體最高堆疊寫入的結束位址（不含）距 APP word 104 bytes。
* [前段固定寫入與兩次清零](v4160-role-first-allocation-prefix.zh-TW.md)皆在低位 RAM。按 Xwchc 解讀，`0x43bb4` 寫容量 byte `0x2000319e`。`0x43bc6` 在判斷配置是否失敗**之前**寫指標槽 `0x2000322c`；若為零就進出口，不執行後面清區塊和寫表。
* 名義配置成功時，payload `P=0x200045b4`。`0x43bda` 清除的長度來自重讀的容量 byte `k`，不是指標；即使只用 `k<=255` 的寬界，寫入終點也不超過 `P+2106`（不含）。`0x43bf2/43bfc` 存的是兩個表基址，目的為固定 word `0x200031c4/31e4`。
* `0x43c08` **重新載入**函式表基址。若它仍是 `P+576`，三筆登記對任何 byte 索引的最高寫入位址均不超過 `0x20004bf3`；穿插的計數寫在 `0x2000319d`。這只證與保存 word 分離，不代表任意索引都在所配置表內。見[三個表項指令](v4160-role-internal-table-writes.zh-TW.md)。

結論限於本體指令及上述清除請求在指定目的與長度執行；不由本體的 frame 推斷所有巢狀呼叫都保持堆疊。特別是 `0x44022` 的讀取回呼會接收一個堆疊目的指標，須另看實際目的和長度。未連接裝置。

以下以 V1.31 carrier 為參數，核對入口、出口、配置失敗分支及兩個 byte 欄位的有限位址界。另重跑上列前段和表項檢查。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('43b3e frame/extent mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def at(pc,h): ck(b[pc-0x40000:pc-0x40000+len(h)//2]==bytes.fromhex(h))
at(0x43d4c,'cd3b');at(0x43b4e,'4111');at(0x43b60,'06c6');at(0x43b66,'22c426c2');at(0x43bc6,'23a6a4222dcd');at(0x43c44,'b2402244924441018280')
E,S,P=0x2000ff50,0x2000ffb8,0x200045b4
ck([E-16+i for i in (12,8,4)]==[0x2000ff4c,0x2000ff48,0x2000ff44] and S-E==104)
for k in range(256): ck(P+576+6*k<=P+2106<S)
for n in range(256):
    for j in range(3): ck(P+576+4*((n+j)&255)+3<=0x20004bf3<S)
print('PASS: frame and exit; 256 clear lengths; 768 table word extents')
```
