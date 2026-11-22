# RF 回呼的已知 APP 設定點晚於參數 774

第三個角色入口內層的 `0x63f26` 不是固定派送器入口。依 V1.31 參考 ROM 與 Xwchc 解碼，外設值低兩位非零、且重新讀取的狀態 byte `0x2000351b` 等於 3 時，才從 `[0x20003550]` 取指標並以 `(17,0,0)` 呼叫。若初始化寫入的狀態 1 保持不變，此呼叫被跳過。即使狀態變成 3，也不能直接代入 APP 回呼 `0x174ee`：還需要設定時間的證據。

沿同一次 APP 初始化、各子呼叫正常返回，順序是 `0x8ec2` 第三角色 → `0x8ef6` 參數 774 → `0x8fdc` 呼叫 `0x175e8`。中間 `0x8f40` 的條件分支只略過一段設定並在 `0x8f5e` 匯合。`0x175e8` 才建立含 `0x174ee` 的設定記錄並交給 `[0x401c4]`。掃描原 APP、候選 ROM 及其第一段 RAM 搬移，直接抵達 `0x175e8` 的受檢編碼只命中 `0x8fdc`。因此**這一次**設定不能供應同輪較早的 `0x63f26`。這不表示當時的指標必為零；前次初始化、其他 writer、間接入口或非同步呼叫均未排除。

參閱[狀態與外設的兩層判斷](v4160-role-63eda-init-gate.zh-TW.md)及[設定記錄到回呼欄位的條件](rf-status-provenance-2026-10-24.md)。複核時在 repo 根目錄依序傳入 decoded APP、V1.31 主區檔：

```python
from pathlib import Path
import sys
sys.path.insert(0,'analysis')
from check_v4160_role_init_args import check as app
from check_v131_role_state_gate import check as gate
from check_v131_descriptor_edges import edges
a,r=(Path(p).read_bytes() for p in sys.argv[1:]); app(a); gate(r)
def ck(x):
    if not x: raise ValueError('callback timing mismatch')
for base,b in [(0x8000,a),(0x40000,r),(0x20000040,r[0x2b0:0x2b0+2957*4])]:
    ck(edges(b,base,0x175e8)==([('0x8fdc','JAL',1)] if base==0x8000 else []))
ck(a[0xf40:0xf44].hex()=='638fe700' and a[0xef6:0xef8].hex()=='8297')
ck(a[0xf644:0xf65c].hex()=='970700009387a7ea3ec89147a30cf1008327441c0a858297')
ck(r[0x23f18:0x23f28].hex()=='b737002083a707550146814545458297')
print('PASS: one direct constructor edge after 774; callback slot and arguments pinned')
```
