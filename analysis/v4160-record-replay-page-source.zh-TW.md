# 重播的 64 bytes：先選頁，再選記錄

接續[重播迴圈](v4160-write-service-record-replay.zh-TW.md)。V1.31 參考 `0x440c2` 不是將指定地址直接讀 64 bytes 的函式。對這個呼叫者，a0 是鍵 `0x7000+i`、a1 是長度 64、a2 是目的緩衝區。進入重播的查找結果 `i` 小於一個無號 byte，因此最多為 254（以正常保留暫存器為前提）。

* 設定 +8 的基址非零且 +56 回呼非空時，`0x442ae..0x442ba` 接受上述鍵，減去 `0x7000`。`0x44228..0x44234` 取設定 +12 的半字頁長 L，算出頁地址 `A=base+i*L`（RV32 算術）。當 `[0x200031c0]==A` 且 `[0x200031bc]` 非零時直接使用快取；否則配置 L bytes，請求 `cfg.read(A,L>>2,buffer)`。回呼返回值不在此處測試；不能只看它就推定資料已讀入。若[APP 設定](v4160-cfg-read-gate-44022.zh-TW.md)及預設頁長仍有效，A 為 `0x08077c00+i*256`，一次讀頁要求 64 個 word，而非 64 bytes。
* 候選 Xwchc 下，第一個記錄標頭位於 buffer+4；標頭 +2 的 byte 應為 `0x5a`，+0 的小端半字應等於完整鍵。命中時以**標頭後四個 bytes 的位置**作為來源，`0x44292..0x44296` 呼叫候選複製函式 `0x20000332(dst, header+4, 64)`；在正常返回及清理後回零。`0x442bc` 的鍵不符路徑改從標頭 +3 取下一位置，不是直接取固定的頁首 64 bytes。
* 基址為零時另有 `0x442d4` 的 RAM 指標路徑，本報告不把它當成已從上述地址讀頁。沒有實機頁內容、快取狀態或安裝版本，不能決定命中的標頭或還原 64 bytes 的值。

重現：傳入相同 V1.31 主區段 BIN；檢查選頁算式指令、表頭三個 Xwchc 載入欄位與複製目標，不執行裝置或模擬完整函式。

```python
import hashlib,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('page source mismatch')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for p,h in [(0x442ae,'21677917e361a7f6b30a5541bdb7'),(0x44228,'03d7c900373b0020b38aea02be9a'),(0x4425e,'83d5c90083a789032a866898156858297'),(0x44288,'85058a052686a2954a85')]:
    ck(raw(p,len(h)//2)==bytes.fromhex(h))
for pc,op,rd,off in [(0x4427c,0x2000,13,2),(0x44282,0x2002,13,0),(0x442bc,0x2000,11,3)]:
    h=int.from_bytes(raw(pc,2),'little'); ck(h&0xe003==op and 8+(h>>7&7)==15 and 8+(h>>2&7)==rd)
    ck(((h>>5&3)*2+((h>>12&1)+(h>>10&3)*8 if op==0x2000 else (h>>10&7)*8))==off)
p=0x44292; u=int.from_bytes(raw(p,4),'little'); j=int.from_bytes(raw(p+4,4),'little'); ck(u&4095==0x97 and j&0xfffff==0x80e7 and (p+(u&0xfffff000)+((j>>20^2048)-2048))&0xfffffffe==0x20000332)
print('PASS: page selection, read arguments, 3 header fields and payload copy target')
```
