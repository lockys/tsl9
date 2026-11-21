# 計時節點到期後是設事件位，不是立即呼叫 handler

接續[首次 16-byte 節點](v4160-first-timer-block.zh-TW.md)。以下假設 V1.31 的 carrier `0x40270` 起始內容按既有映射複製到 RAM `0x20000000`，且採 Xwchc 解讀。以下 PC 除特別註明外均標 carrier 位置。

1. `0x40774` 讀 head；空表直接離開。`0x407ac` 判斷的是節點 **+2 的 event 半字**，不是 +1 的旗標。event 為零會摘除並釋放，不取時鐘。首次節點的 `0x2000` 非零，因此會從 `0x200031e0` 取回呼並呼叫；之後才載入節點 +8 的期限 `D`。
2. 設返回的無號 tick 為 `T`。若 `T >= D`，差值為 `T-D`；否則從設定 `0x20003238` 重讀週期 `M`，差值為 `(M-D+T) mod 2^32`。**差值小於 30000000** 才走到投遞；等於 30000000 已走跳過投遞的分支。名義 `M=0xffffffff`、`0<=T,D<M` 時，就等於檢查 `(T-D) mod M < 30000000`。這是一個到期視窗，不是單純 `T>=D`，也不是已知的秒數。
3. 命中視窗先清 `0x200031ac` 的 word，再重讀節點 event 與 ID。`0x407f4` 必須用**執行位址** `0x20000584` 解 AUIPC/JALR：目的為 `0x4354a`。若讀到 `(ID=3,event=0x2000)` 且 ID 小於目前登記數量，從 `0x200031e4` 取事件表指標 `P`，執行 `U16[P+6] |= 0x2000` 並返回 0。若 ID 不合法則返回 3，不寫表。**同一事件多次設位不會累計次數**，也沒有在這裡呼叫 APP handler。
4. `0x407fc` 不檢查投遞回傳值，而是重新載入節點 +4。若仍為初始零，會將一次性節點摘鏈後交給釋放函式；不能由節點已移除反推投遞成功。未證明實機何時進入本輪掃描或何時消費該事件。

重現：以 V1.31 carrier 為唯一參數。固定關鍵指令，從編碼取比較常數及呼叫目的；比較跨週期邊界和全部事件半字的設位結果。不是實機或全函式模擬。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('due/post evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p): return int.from_bytes(b[p:p+4],'little')
def win(p,h): ck(b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h))
win(0x7ac,'3e2099ef5c44'); win(0x7cc,'83a70a1e82971c443307f5406376f50003a749001d8f2a97'); win(0x7e8,'63eae606232809002e200820'); win(0x7fc,'5c405844b1c7'); win(0x850,'23a4e41e9db7')
limit=(w(0x79c)&~4095)+(w(0x7e4)>>20); ck(limit==29999999)
u,j=w(0x7f4),w(0x7f8); ck(u&4095==151 and j&0xfffff==0x80e7); ck((0x20000584+(u&~4095)+((j>>20^2048)-2048))&0xfffffffe==0x4354a)
win(0x355e,'0347d7196370e50237360020131715000325461e3a951a21d98d0ea1'); win(0x3582,'23a6d7200d458280')
M=0xffffffff
for d in (0,1,1920000,M-limit,M-2,M-1):
    for elapsed in (0,1,limit-1,limit,limit+1,M-1):
        t=(d+elapsed)%M; diff=t-d if t>=d else (M-d+t)&M
        ck(diff==elapsed and (diff<=limit)==(elapsed<30000000))
for old in range(65536):
    posted=old|0x2000; ck(posted&0x2000 and posted&0xdfff==old&0xdfff and posted|0x2000==posted)
print('PASS: relocated post target 0x4354a; 36 deadline cases; 65536 prior event masks')
```
