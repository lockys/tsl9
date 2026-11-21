# 0x20003454：誰能把空串列變成非空？

在 V1.31 參考映像，啟動清零若正常完成，串列頭是從 `0x20002ef8` 起第 344 個被清零的 word（共 456 個）。但零並非不變量。

* `0x57962` 以 488、611 作參數呼叫配置函式；`0x57980` 將傳回值保存到 s0，另呼叫清零函式後才測試 s0。若正常返回、s0 保持非零且舊 head 為零，`0x5799e` 跳至 `0x579cc`；`0x579d0` 將 s0 寫入 head，下一條寫到相鄰的 tail。兩者分別是 `0x200033b8+156` 和 `+160`。此路徑依候選 Xwchc 解讀，不代表設備已配置此節點。
* 刪除路徑 `0x57a4a` 不應算成從空串列新增節點：先讀 head，為零即在 `0x57a64` 跳走；在非空路徑才可能由 `0x57a70` 寫入下一節點，或由 `0x57a90` 寫零。
* 在整份 carrier 每兩 bytes 掃描四-byte `jal ra` 編碼，指向 `0x57962` 的是 `0x59e70`、`0x608a6`。它們位於 `0x59e64`、`0x6089a` 的函式前綴；`0x60856` 在 `0x60898` 已返回，**不會因線性相鄰而執行 `0x608a6`**。掃描不是完整呼叫圖，不能排除間接呼叫或其他寫入。
* `0x5362e` 的 296-byte 清零也涵蓋 head，但從 `0x55bde` 進入該清零時，入口讀值已發生，不能倒推入口前的 head。尚須定位兩個配置呼叫者在此時間窗的來源；head 非零本身仍不保證查找命中。

以 V1.31 carrier 檔案為唯一參數重現：

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes(); base=0x40000
def ck(x):
    if not x: raise ValueError('head writer evidence mismatch')
def raw(p,h):ck(b[p-base:p-base+len(bytes.fromhex(h))]==bytes.fromhex(h))
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
raw(0x40292,'b737002037370020938787ef130747616373f700828023a007009107d5bf');ck(range(0x20002ef8,0x20003618,4)[343]==0x20003454)
raw(0x57964,'930530261305801e');raw(0x57980,'2a849790fa1fe780a0a101450dc8');raw(0x5798e,'b73400209387843b83a6c7099384843b9dc6');raw(0x579cc,'85471ea423ae840823a0840a');ck(0x20003000+952+156==0x20003454)
raw(0x57a56,'83a6c70906c60147b6871304843ba9cb');raw(0x57a6e,'9842232ee408');raw(0x57a90,'232e0408');raw(0x60896,'410182800111');hits=[]
for i in range(0,len(b)-3,2):
    w=int.from_bytes(b[i:i+4],'little');v=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1
    if w&4095==239 and base+i+(v^0x100000)-0x100000==0x57962:hits.append(base+i)
ck(hits==[0x59e70,0x608a6]);print('PASS: startup word 344; head and tail stores; two direct call encodings')
```
