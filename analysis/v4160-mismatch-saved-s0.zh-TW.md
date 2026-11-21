# 讀回不相等：暫存區生命週期是否寫到 APP 保存的 s0？

接續[四 byte 讀取](v4160-cfg56-stack-read.zh-TW.md)，只考慮比較不等後到 `0x44022` 返回。要保護的是 `[0x2000ffb8,0x2000ffbc)`。以下是原 APP 配合 V1.31 參考程式、Xwchc 解讀與既有名義堆疊的 CPU 邏輯寫址，不是裝置上的儲存操作。

|階段|目的範圍與前提|
|---|---|
|`0x4406a` 配置|入口 SP `0x2000ff20`；配置器扣 16，保存 s0/ra 的 word 分別在 `0x2000ff18/1c`。正常分割只改名義 arena 的 header、可用量半字及外設。若返回零，`0x44076` 仍先寫零到 `0x200031bc`，但不填值、不進三輪、不釋放。配置失敗前若另呼叫非零的未知失敗回呼，其作用不在此結論內。|
|成功、填值與三輪|按[暫存區寫址](v4160-44060-temp-buffer-stores.zh-TW.md)，重讀長度仍是 256 才能沿用配置界限。填值寫 `[P,P+256)`；每輪的 word 寫在**當次重讀的 P 本身**，不是 `P+4*i`。三次 APP 回呼則讀 P 並寫三個不同目的區段，名義聯集 `[0x08077c00,0x08077f00)`。|
|APP 回呼本身|[22 處 store](v4160-cfg60-heap-separation.zh-TW.md) 中的外設地址與 APP 保存槽分離。每次回呼保存三個 word 至 `0x2000ff1c/18/0c`，會重用先前已返回的配置器 frame，不是配置器仍在執行。這兩組堆疊寫入的結束位址至 APP 保存槽有 **152 bytes**。|
|退出與釋放|按[釋放寫址](v4160-44098-release-write-set.zh-TW.md)與[256 個配置布局](v4160-second-release-table.zh-TW.md)，正常次序是清命中塊 tag、只與後塊合併、更新可用量，而不是將 payload 清零。呼叫端正常返回後清 `0x200031bc/31c0` 兩個 word。有效 header 全在 arena 內。|

所以，若長度、回呼綁定、每次重讀的 P 和 heap 串列均保持上述條件，這條分支沒有已辨識的 CPU 寫入碰到 APP 保存槽。三次回呼不保證實際發生或返回；不能由第一次配置成功推出稍後的指標和 header 必然有效。亦不涵蓋中斷、DMA 或外設副作用。

補充檢查接受 V1.31 carrier，核對配置器 frame 的三條指令，將上述名義布局與三輪寫址投影到同一個受保護區間；不是完整指令模擬。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('mismatch branch extent')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x2b0:0x2ba].hex()=='411122c4b747024006c6')
S=0x2000ffb8; E=0x2000ff20; H=0x200045ac; end=0x2000b184
def separate(p,n): return p+n<=S or S+4<=p
frames=[E-16+8,E-16+12,E-32+28,E-32+24,E-32+12];ck(all(separate(p,4) for p in frames) and S-max(frames)-4==152)
for c in range(256):
    k=14+3*((c>>2)+(c&3)); n=H+8+((576+6*k+3)&~3); p=n+8; tail=p+256
    ck(0x200043ac<n<p<tail<end and tail+8<=end<S)
    ck(all(separate(x,z) for x,z in [(n,8),(tail,8),(p,256),(p,4),(0x200031a2,2),(0x200031bc,8)]))
for i in range(3):
    for j in range(0,256,4): ck(separate(0x08077c00+i*256+j,4))
print('PASS: 256 heap layouts; 192 destination words; allocator/callback stack gap 152 bytes')
```
