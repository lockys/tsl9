# 第二次配置釋放：三個 header store 都在同一個八位元組內

接上[回呼返回後仍交出 P](v4160-44090-reloaded-buffer.zh-TW.md)，採用[第二次配置的名義布局](v4160-second-allocation-frontier.zh-TW.md)：第一次配置成功且其 header H 仍標為已用，第二次配置的 256-byte payload 恰為 P=N+8，尾塊 F 仍空閒，串列與游標未被干擾。依[只向後合併的分支](v4160-second-release-table.zh-TW.md)，V1.31 參考 RAM 程式先在 `0x20000178` 清 `N+6` 半字，再於 `0x200001ce` 寫 `N+4` 半字、`0x200001d0` 寫 `N+0` 的 word。**三筆合計正好覆蓋 `[N,N+8)`，不寫 P 的 payload，也不寫被移出串列的 F header。**

逐一代入 256 個設定 byte（不代表 256 個不同布局），N 最小 `0x20004848`、最大 `0x20004cec`。每筆 header 寫入完整落在名義 heap `[0x200043ac,0x2000b184)`；保存任務表基址的 `0x200031c4` 不在內。可用量另在 `0x200031a2` 半字更新兩次：加 256，再加移除 header 的 8；總效果為 `(old+264) mod 65536`。另有外設控制字的寫入與還原，不應說整個函式只寫八個 bytes。這是初始化條件成立時的直接寫址，不是實機 RAM 快照；僅知 P 是合法指標並不足以推出合併方向。

重現：傳入 V1.31 主段。以啟動複製映射取三個 header store，依 RV32 和參考 Xwchc 解碼目的、寬度與來源暫存器；另核對兩段記帳指令。分支選擇沿用上面的布局分析，非通用 CPU 重播。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('release footprint mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def op(p,n): return int.from_bytes(b[0x270+p:0x270+p+n],'little')
w,h,c=op(0x178,4),op(0x1ce,2),op(0x1d0,2)
ck(w&0x707f==0x1023 and h&0xe003==0xa002 and c&0xe003==0xc000)
rows=[(w>>15&31,(w>>25<<5)|(w>>7&31),2,w>>20&31),(8+(h>>7&7),8*(h>>10&7)+2*(h>>5&3),2,8+(h>>2&7)),(8+(c>>7&7),8*(c>>10&7)+4*(c>>6&1)+64*(c>>5&1),4,8+(c>>2&7))]
ck(rows==[(15,6,2,0),(15,4,2,13),(15,0,4,14)])
ck(b[0x270+0x180:0x270+0x188].hex()=='2e97420741837aa1' and b[0x270+0x1d2:0x270+0x1d8].hex()=='7e22a1077ea2')
ns=[]; e=0x2000b184
for i in range(256):
    k=14+3*((i>>2)+(i&3)); n=0x200045ac+8+((576+6*k+3)&~3); p=n+8; f=p+256
    dst=[n+d+j for _,d,size,_ in rows for j in range(size)]
    ck(sorted(dst)==list(range(n,p)) and 0x200031c8<=0x200043ac<=n<p<f<f+8<e); ns.append(n)
ck((min(ns),max(ns))==(0x20004848,0x20004cec))
for old in range(65536): ck((((old+256)&65535)+8)&65535==(old+264)&65535)
print('PASS: 3 decoded header writes cover exactly N..N+7; 256 layout inputs; 65536 accounting inputs')
```
