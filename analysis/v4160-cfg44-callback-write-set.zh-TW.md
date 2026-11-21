# APP `0x197f0` 會改寫配置失敗回呼嗎？

接續[設定 +52 的初值](v4160-allocator-failure-slot-origin.zh-TW.md)。這次只問**另一個**設定欄位 `+44` 指向的 APP 函式有哪些 CPU 寫址，分析原始 v4.1.60 BIN，沒有連設備。

`0x197f0..0x1995a` 先保存暫存器與兩組外設狀態，設定外設，輪詢 `0x40012400` 的 bit 1。若等到非零，取 `[0x4001244c]` 的低 16 位，重設外設並逐一寫回保存值，再返回取樣值。輪詢可能不結束。「寫回」只描述指令，不保證外設狀態可逆。

| 呼叫目標（依首次出現排序） | 本次實參和所選分支的寫址 |
|---|---|
| `0x8520` | 目的為 frame SP+32、值 0、長度 32。若入口 SP 為 16-byte 對齊、區間不迴繞，`0x8538..0x8542` 兩輪清零 `[SP+32,SP+64)`。此處 SP 已扣 128。 |
| `0x19124`、`0x1908c` | 分別寫 `0x40021018`、`0x40021004`。 |
| `0x188e2`（呼叫兩次） | 實參 `B=0x40012400`；保存 ra 至自己的 stack，先呼叫再尾跳 `0x19160`，兩次皆寫 `0x4002100c`。 |
| `0x1892e`、`0x18986`、`0x18a98`、`0x18a6e` | 依序寫 `B+4/8/44`、`B+8`、`B+4`、`B+8`。`0x1892e` 從 stack 設定讀值，不向這個設定指標寫入。 |
| `0x189ae`、`0x18996` | 前者以 `(B,16,1,7)` 選 `B+12`、`B+52`，後者寫 `B+8`。 |
| `0x18a8e`、`0x18a66` | 只讀：前者在輪詢路徑測 bit 1；後者取樣，兩者均無 store。 |

本體有 26 個 stack store 位置，另外 16 處 word store 寫回 `0x40021018/0x40021004` 與 `B+4..B+56`（每 4 bytes）。在正常返回、暫存器依所選路徑保留、stack 與目標 RAM 分離的情況下，**本回呼及上述子呼叫不會直接寫入 `0x20003220`**。這不需要假設外設會回報就緒；未就緒的輪詢本身不寫 RAM。這不是中斷、DMA、外設副作用或整段初始化都保持該槽的證明。

以下檢查本體的直接 JAL 和 store 清單，並核對兩個只讀 helper 的完整位元組；子函式分支語意另按上表靜態解碼，不是 CPU 模擬。以原 APP BIN 路徑為參數：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def need(ok):
    if not ok: raise ValueError('APP ledger mismatch')
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
pc=0x197f0; calls=[]; stack=[]; io=[]
while pc<0x1995c:
    i=pc-0x8000; w=int.from_bytes(b[i:i+4],'little'); h=w&65535
    if h&3==3:
        if w&127==0x6f:
            d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
            need(w>>7&31==1); calls.append(pc+(d^0x100000)-0x100000)
        if w&127==0x23:
            base=w>>15&31; off=(w>>25)*32+(w>>7&31); size=1<<(w>>12&7)
            (stack if base==2 else io).append((base,off,size))
        pc+=4
    else:
        if h&0xe003==0xc002: stack.append((2,4*(h>>9&15)+64*(h>>7&3),4))
        need(h&0xe003!=0xc000); pc+=2
need(calls==[0x8520,0x19124,0x1908c,0x188e2,0x1892e,0x18986,0x18a98,0x18a6e,0x189ae,0x18996,0x18a8e,0x18a66,0x188e2])
need(sorted(stack)==sorted([(2,n,4) for n in list(range(76,128,4))+list(range(4,52,4))]+[(2,52,1)]))
need(sorted(io)==sorted([(15,24,4),(15,4,4)]+[(8,1024+n,4) for n in range(4,60,4)]))
need(b[0x10a8e:0x10a98].hex()=='08416d8d3335a0008280' and b[0x10a66:0x10a6e].hex()=='6845420541818280')
print('PASS: 13 call sites, 26 stack stores, 16 peripheral restores, 2 read-only helpers')
```
