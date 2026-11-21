# 首次排程回到 APP：區分返回值、返回地址與角色表基址

**結論。** 令 `S` 為 APP `0x19b16` 進入時的 s0，而不是預設常數。按下列條件，回到 `0x8eb0` 時 `s0=S`。名義首次插入成功另給 `a0=1`，但 APP **並不用這個 1 決定是否繼續**。即使 `S` 本來不是 `0x40000`，正常恢復也不會將它變成 `0x40000`。

|區段|可由指定指令與布局得到的結果|尚需的前提|
|---|---|---|
|APP 尾跳|`19b3e` 載回 `S`，`19b54` 尾跳而不改 ra。|登記與校時已返回，APP 的保存槽完好；s1 指向參考表。|
|排程、查找|`[0x40058]` 選 `43728`；重新保存 s0、ra。名義 `(3,8192,192000)` 通過檢查；空表查找返回零且不寫節點。|參考映射及 Xwchc 適用、ID/計數及時鐘綁定保持，時鐘輪詢返回；第一次讀 head 為零。|
|配置、插入|首塊分割得到 `P=0x200043b4`。配置的 12 次及空表安裝的 8 次直接寫入均不覆蓋保存槽。|小游標與空閒首塊有效，配置成功，**第二次**讀 head 仍為零。|
|共同返回|`437b4/b6` 分別重載 ra、s0，唯一 `ret` 在 `437c8`。不要求 s0 在函式內一直保持 `S`。|SP 如期恢復、讀寫成功、有效保存值未被中斷、其他執行者或外設改寫。|

**哪些條件可以放寬？** 空表與配置成功是用來確定「這次建立首筆節點」及其寫址的充分條件，不是恢復 s0 的必要條件。若在入口因 ID 或時鐘檢查失敗而正常返回，也經同一恢復序列。若查找命中、追加到非空表、配置失敗並叫到未知回呼，返回指令仍相同，但不能沿用首次空表成功的寫址證明。若輪詢不返回，便沒有可談的 `0x8eb0` 狀態。

**APP 端的獨立交叉檢查。** `8eb0` 無條件呼叫 `907a`。由 `907a` 到 `908c` 沒有指令讀傳入的 a0；`908c` 的 `auipc a0` 覆蓋它，`9090` 再加位移，令 `9094` 呼叫的第一參數為 `0x2000be08`，和排程回傳 0 或 1 無關。`90a8` 保存的低 byte 是稍後 `90a2` 呼叫的結果，不是排程結果。

重現入口：[APP 尾跳及保存槽](v4160-role-tail-s0-slot.zh-TW.md)、[查找前寫入](v4160-head-before-lookup.zh-TW.md)、[首次請求](v4160-first-schedule-request.zh-TW.md)、[表頭重讀](v4160-first-timer-head-reload.zh-TW.md)、[首塊布局](v4160-first-timer-block.zh-TW.md)、[配置寫址](check_v131_first_alloc_stores.py)、[節點寫址](v4160-first-node-frame-separation.zh-TW.md)、[返回圖](check_v131_scheduler_return_graph.py)、[APP 續段](v4160-init-reload-to-role-slot.zh-TW.md)。這是九項離線檢查的條件組合，不是一次連續執行或實機 ROM 證明。

以下檢查接受原 decoded APP，固定覆蓋 a0 前的直線區段並從指令算出第一參數。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('scheduler status consumer mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(b[0x107a:0x108c].hex()=='411122c4370404003c4406c61306400b8145')
u,i=(int.from_bytes(b[j:j+4],'little') for j in (0x108c,0x1090))
ck(u&4095==0x517 and i&0xfffff==0x50513 and b[0x1094:0x1096].hex()=='8297')
ck((0x908c+(u&0xfffff000)+((i>>20^2048)-2048))&0xffffffff==0x2000be08)
ck(b[0x10a2:0x10ac].hex()=='8297b24022442383a10a')
print('PASS: incoming scheduler status overwritten before first call; later result byte stored after second call')
```
