# 零基址：初始化不配置，寫入服務可按需配置

[讀取服務](v4160-base-zero-row-read.zh-TW.md)會查 `B = U32[0x200031bc]`。V1.31 參考映像下，這個指標不能單從 `cfg+8 == 0` 推定：

| 時點 | 指標如何改變 |
|---|---|
| 初始化 `0x43b80` | 請求把 `[0x2000319c,0x200031c4)` 的 40 bytes 填零。若參考 fill 正常完成，B 所在的四個 bytes（偏移 32..35）全為零。 |
| 初始化內 `0x44022` | `0x4402e` 讀 cfg+8。為零時，`0x44036` 不跳，直接返回 **1**；除自身堆疊保存外不寫記憶體，不經配置器。這個 1 不是讀取服務的返回碼。 |
| 首次讀取，B 仍為零 | `0x442d4` 的 RAM 分支返回 **10**，不配置、不複製記錄。 |
| 寫入服務 `0x4435c`，基址與 B 都為零 | 先從 cfg+14 取 byte、cfg+12 取 halfword，將乘積低 16 位作為大小、78 作為第二參數呼叫 `0x20000040`。`0x4459e` 先把返回值寫到 B；零走返回 10，非零跳回 `0x4454c` **重讀 B** 再檢查記錄，不以配置成功當作命中。若 B 原本非零，跳過配置。 |

原 APP 的[設定基址](v4160-cfg-read-gate-44022.zh-TW.md)是 `0x08077c00`。以上是另一個分支，不代表原 APP 一定選它、配置內容已初始化或後續一定讀得到。假設參考 RAM 程式已按預期複製、採 Xwchc、堆疊分離；未排除其他寫入或非同步改變。

離線核對（參數為 V1.31 carrier）：

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('cache lifecycle mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def window(pc,s):
    v=bytes.fromhex(s); ck(b[pc-0x40000:pc-0x40000+len(v)]==v)
window(0x43b76,'1305c419 13068002 8145 97d0fb1f e780c081')
ck(0x43b80+0x1ffbd000-2020==0x2000039c and set(range(32,36))<=set(range(40)))
window(0x4402e,'8847 06ce 26ca 4ac8 01e9 0545 f240 6244 d244 4249 0561 8280')
window(0x44382,'638d0a1a'); window(0x4453c,'373a0020 9307ca19 9c53 130aca19 95cf 03250a02')
window(0x44586,'6824 5e24 9305e004 3305f502 4205 4181 97c0fb1f e780a0aa 2320aa02 4df5 ddb3')
for o,kind,rd,d in [(0x4586,0x2000,10,14),(0x4588,0x2002,15,12)]:
    h=int.from_bytes(b[o:o+2],'little'); ck(h&0xe003==kind and 8+(h>>7&7)==8 and 8+(h>>2&7)==rd)
    ck(2*(h>>5&3)+8*(h>>10&(3 if kind==0x2000 else 7))+(h>>12&1 if kind==0x2000 else 0)==d)
ck(0x44596+0x1ffbc000-1366==0x20000040 and 0x20003000+412+32==0x200031bc)
window(0x4438a,'2945'); print('PASS: init fill, early return, RAM write branch, two Xwchc operands, allocation and pointer store')
```
