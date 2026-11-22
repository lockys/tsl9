# 校準回呼槽：從 64-byte 初始化複製到第一個巢狀回呼

初始化本身確實會寫 `0x2000321c`：它是 `0x200031ec` 起算的 +48，並非零寫入槽。成功複製會把 [APP 填入的 `0x197b8`](v4160-task-clock-callback-origin.zh-TW.md) 寫到這四個 byte。以下從複製正常返回開始，不把「初值已知」當成「首次校時讀值已知」。

1. V1.31 參考 `0x43cf8..0x43d32` 的八個條件式預設寫入，按指令順序是 `+12:2、+14:1、+16:2、+15:1、+18:1、+19:1、+20:1、+22:1`（位移:寬度，採 Xwchc 解碼）。沒有一筆碰 `+48..51`。
2. 緊接的 `0x43d34` 載入的是 **+44**，不是 +48；若仍是初始化綁定，`0x43d38` 呼叫 APP `0x197f0`。核對這個函式本體 `[0x197f0,0x1995c)`：26 處直接寫堆疊，16 處直接寫外設。若各子呼叫保持 SP、s0，外設 word 寫入為 `0x40021018、0x40021004` 及 `0x40012404..0x40012438`（每 4 bytes）。沿用 `0x9008` 入口 SP=`0x20010000`，當時尚未進 `0x43b3e`，故回呼 SP 是 `S−176−128=0x2000fed0`，直接 stack 寫入都在這個 128-byte frame 內。
3. 若 +44 回呼正常返回，`0x43d3e` 將其結果低半字寫 `0x200031a4`；略過或返回都會在 `0x43d48` 寫 byte 至 `0x200035f5`。兩者也不碰回呼槽。接下來才在 `0x43d4c` 進入 `0x43b3e`。

**邊界：**本體有 13 個直接呼叫點，不能把本體無重疊當成這些子呼叫也無重疊。特別是 `0x19814` 以 frame+32、0、32 呼叫 `0x8520`，以及 `0x19896` 同時傳入外設基址與 frame+32；它們是下一層需分別追蹤的目的指標。以上為條件式靜態結果，非裝置觀測。

重現本體統計：以 decoded APP 與 rasm2 執行檔路徑為兩個參數；八個預設 store 的解碼方式見[相鄰 +52 欄位驗證](v4160-allocator-failure-slot-origin.zh-TW.md)。

```python
from pathlib import Path
from hashlib import sha256
from collections import Counter
import subprocess,sys,re
a=Path(sys.argv[1]).read_bytes()
if sha256(a).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP mismatch')
s=subprocess.check_output([sys.argv[2],'-a','riscv','-b','32','-s','0x197f0','-D',a[0x117f0:0x1195c].hex()],text=True)
w=re.findall(r'\s(sb|sh|sw) \w+, (\d+)\((\w+)\)',s)
if Counter(r for _,_,r in w)!={'sp':26,'a5':2,'s0':14} or s.count('jal ra,')!=13 or 'invalid' in s: raise ValueError('instruction inventory mismatch')
if sorted(int(d) for _,d,r in w if r=='s0')!=list(range(1028,1081,4)) or sorted(int(d) for _,d,r in w if r=='a5')!=[4,24]: raise ValueError('peripheral offsets mismatch')
if not all(0<=int(d)<=128-{'sb':1,'sh':2,'sw':4}[op] for op,d,r in w if r=='sp'): raise ValueError('frame mismatch')
print('PASS: 26 stack stores, 16 peripheral-base stores, 13 direct calls')
```
