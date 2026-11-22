# 派送後的可選回呼：槽 0 的四個登記點

`0x20000936` 取的是 `[0x200031c8]`，不是任務 handler 表，也不是索引 2 的時鐘回呼。槽為零便略過。非零時 `0x2000093c` 間接呼叫；在 s2 仍保有基底並正常返回時，`0x2000093e` 清的是**回呼槽本身**，不與游標或任務數 `[0x2000319c,0x2000319e)` 重疊。它也不會先確認槽內仍是剛呼叫的值。

在 V1.31 參考 carrier 內，四處直接呼叫 `0x43b28` 前均設 `(a0,a1)=(0x55480,0)`。這個設定函式以 `a1` 為索引寫入五槽表。這提供一個具體候選，不代表該值在執行時仍留在槽內，也不代表只有四個寫入者。

若實際呼叫這個候選，入口先保存八個 word 到堆疊，從 `0x2000341c` 讀物件指標。在 Xwchc 解讀下，`0x554c0` 讀物件 `+11` 的狀態 byte。索引為 `(state+110)&255`；狀態 146..158 使用 13 格跳轉表，其他 243 值在 `0x55634` 呼叫 `0x63e58`。到上述分流為止，若堆疊與排程欄位分離，沒有直接寫游標或任務數。**尚未排除分支本體或下層呼叫改寫**，也不保證回呼返回。

複核：以下以參考 carrier 為唯一參數，只讀取位元組，不執行韌體。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('slot 0 evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(o,h):
    v=bytes.fromhex(h);ck(b[o:o+len(v)]==v)
def word(o):return int.from_bytes(b[o:o+4],'little')
def jal(o):
    x=word(o);ck(x&4095==0xef);d=(x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    return 0x40000+o+(d^1048576)-1048576
raw(0x270+0x936,'8327891c81c782972324091c0347c41983471a00');raw(0x3b28,'914763e9b700b73700208a059387871cbe9588c18280')
for o in (0x142f2,0x146ea,0x150aa,0x21e9a):
    h='375505008145'+('b8db' if o==0x21e9a else '')+'13050548';raw(o-len(bytes.fromhex(h)),h);ck(jal(o)==0x43b28)
raw(0x15480,'797126d2b73400209387843b22d4e0534ad052cc56ca37ea060037390020b73a00204ece5ac806d69384843b130aca5013094951b7390020938aca1e130b44013c3431479387e70693f7f70f6364f7168a07d2979c438287')
ck(jal(0x15634)==0x63e58);h=word(0x154c0)&65535
ck(((h>>12&1)|((h>>5&3)<<1)|((h>>10&3)<<3))==11)
targets=[word(0x2e50c+4*i) for i in range(13)]
ck(targets==[0x55552,0x5557e,0x55688,0x554d8,0x55720,0x55800,0x5579c,0x5583c,0x5587c,0x554ea,0x5563a,0x555e4,0x557e8]);ck([s for s in range(256) if ((s+110)&255)<13]==list(range(146,159)))
print('PASS: 4 slot-zero registrations; 13 distinct table targets; 243 default states')
```
