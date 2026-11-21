# 初始化到排程入口：串列頭的零值可否傳遞？

**名義正常路徑可以，裝置實況未知。** 目標是四個 bytes `[0x200031e8,0x200031ec)`。條件是 V1.31 參考映射及 Xwchc 解讀成立、初始化使用既有分析的 APP 設定與 stack、名義配置成功且指標維持有效、指定回呼正常返回、外設或中斷沒有另外改寫 RAM。按時間串接既有寫入分析，而非將 RAM 預設為零：

1. `0x43b42` 明確寫零。[第一次配置前](v4160-role-first-allocation-prefix.zh-TW.md)的兩次固定 fill 都在 head 之前；[配置與釋放](v4160-second-release-table.zh-TW.md)的有效 header 與 payload 均在 `0x200043ac` 以上，記帳半字在 `0x200031a2`。讀回不一致的分支另需[三次 APP 回呼](v4160-cfg60-heap-separation.zh-TW.md)維持名義目的地；不能把失敗回呼也算成無寫入。
2. [內部登記](v4160-role-internal-table-writes.zh-TW.md)寫計數與表項，不執行 handler。其後[APP 登記](v4160-first-app-registration-order.zh-TW.md)在名義條件下寫表項 `0x20004800`、計數 byte `0x2000319d`、APP task byte `0x20004184`。均與 head 分離。
3. APP 在 `0x19b96` 呼叫 `0x19248(1)`，再在 `0x19ba0` 呼叫 `0x19220(0)`。兩者都先保存 ra 及輸入、呼叫 `0x1919c` 設定控制位，寫入兩個半字，再尾跳 `0x191ae` 清控制位。以兩者入口 SP=`0x2000ffb0` 計，保存位置同為 `0x2000ffac/ff9c`。四個資料半字及兩個控制位寫入點全部在外設，而非 RAM。這補上四次輪詢之間的兩個巢狀呼叫。
4. [校準](v4160-task-clock-callback-origin.zh-TW.md)只在指定配置下排除 stack 與外設寫入；[時鐘設定](v4160-task-clock-postcopy.zh-TW.md)更新的回呼指標 word 在 `0x200031e0`，16-byte 複製始於 `0x20003234`。兩者都不是 head。連同[排程器入口到查找](v4160-head-before-lookup.zh-TW.md)，若上述各段成立，第一次查找讀零，進入 16-byte 配置分支，而非更新已有節點。這不保證配置成功或一定成為表頭；配置後有第二次讀取。

本輪新增的獨立核對如下（參數為 decoded APP）。檢查兩個 caller、四個直接/尾跳目的、stack 與六個半字 store。此測試只驗第 3 段，不宣稱執行整條鏈。

```python
from pathlib import Path
from hashlib import sha256
import sys
a=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('clock setup write mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def ins(p,n=4): return int.from_bytes(a[p-0x8000:p-0x8000+n],'little')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def jal(p,rd):
    x=ins(p); ck(x&4095==(rd<<7|111)); return p+sx((x>>31<<20)|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
ck(ins(0x19b94,2)==0x4505 and ins(0x19b9e,2)==0x4501)
ck([jal(p,r) for p,r in [(0x19b96,1),(0x19ba0,1),(0x1924e,1),(0x1926e,0),(0x19226,1),(0x19244,0)]]==[0x19248,0x19220,0x1919c,0x191ae,0x1919c,0x191ae])
ranges=[]
for p in (0x19220,0x19248):
    ck(ins(p,2)==0x1101)
    for q in (p+2,p+4):
        x=ins(q,2); ck(x&0xe003==0xc002); ranges.append((0x2000ffb0-32+(x>>9&15)*4+(x>>7&3)*64,4))
ck(ranges==[(0x2000ffac,4),(0x2000ff9c,4)]*2)
for l,p in [(0x1919c,0x191a8),(0x19254,0x19262),(0x19254,0x19268),(0x191ae,0x191c0),(0x1922c,0x19238),(0x1922c,0x1923e)]:
    x=ins(p); u=ins(l); ck(u&127==55 and x&0x707f==0x1023 and (u>>7&31)==(x>>15&31)); ranges.append(((u&~4095)+sx((x>>25)*32+(x>>7&31),12),2))
ck([p for p,n in ranges[4:]]==[0x40002804,0x40002808,0x4000280c,0x40002804,0x40002818,0x4000281c]); ck(all(p+n<=0x200031e8 or p>=0x200031ec for p,n in ranges))
print('PASS: 6 call edges; 4 frame stores; 6 peripheral halfword store sites; none overlap list head')
```
