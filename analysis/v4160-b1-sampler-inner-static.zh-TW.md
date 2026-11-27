# v4.1.60：sampler 內層 bit selector 與保存界線

本階段展開 [sampler](v4160-b1-sampler-static.zh-TW.md) 迴圈內唯一的 callee。全程離線，只核對原始位元組、operands、不可變 CFG 與 host bitstring／scalar 算術；沒有執行或模擬目標 ISA、RAM、provider、clock、scan 或硬體。

[驗證程式](check_v4160_b1_sampler_inner_static.py)及 [JSON ledger](v4160-b1-sampler-inner-static.json)保存完整函式與呼叫串接證據。

| 候選 | FLASH 原始範圍 | first-copy 對應 RAM 範圍 | bytes／指令 |
|---|---|---|---|
| V131 | `[0x42ec0,0x42f18)` | `[0x20002c50,0x20002ca8)` | 88／31 |
| V140 | `[0x42f4c,0x42fa4)` | `[0x20002c9c,0x20002cf4)` | 88／31 |

新增 **176 bytes、62 條指令**；所有位元組均符合原始 sparse HEX，不以補零填缺口。重用兩份 sampler 共 332 bytes，不重算新增覆蓋，也不提高既有 C 重建覆蓋率。mapping 僅為候選 first-copy 對應，不證明已安裝的 RAM 相同。

## 輸入來源與先行 stores

令 V131 `F=0x20003540`、`C=0x20003560`；V140 對應地址加 80。函式不使用入口 A0／A1／A2 作輸入，而是依序讀取：

1. fresh byte C+13；
2. fresh byte F+27；
3. captured word F+20，以下稱 mask。

計算 proposed index `J=(C13+F27)&31`，**先**向 F+1 寫 byte J，再向 C+13 寫 byte J，之後才測試 captured mask 的 bit J。若該位為 1，直接普通 RET，不讀 divisor。

## unset candidate 的 fallback

bit J 為零時，讀取 fresh byte C+17 作 divisor d，使用原始 unsigned `REMU`：

```text
d != 0：rank = J % d
d == 0：rank = J（RV32 unsigned REMU 的除零結果為 dividend）
```

這是候選 RV32 指令語義與 encoding 合約，不是實際執行除零指令，也不把 d=0 當成 trap 或任意補值。

接著掃描 **captured mask** 的 bits0..31，不重新讀 mask。ordinal 只在遇到 set bit 且尚未命中 rank 時遞增。若 rank 對應某個 set bit，向 F+1 寫該 bit index 並 RET；若掃描耗盡則 RET，不作 replacement。

因此：

- 最多檢查 32 個 bit positions；不會以 index32 作 shift。index 與 set-bit ordinal 的 byte mask 不會在這個範圍內 wrap。
- fallback replacement **只改 F+1**，C+13 仍是 proposed J。例如 mask=0x82、J=2、d=2 時，rank=0，F+1 可被替換為 1，但 C+13 仍為 2。
- rank 不存在時，F+1 保留原先 J；若 mask=0 或 divisor／popcount 不匹配，不能保證輸出是 set bit。例如同一 mask／J 而 d=0，rank=2 超過兩個 set bits，保留 unset J。
- 若另有證據證明 `d==popcount(mask)>0`，即可保證最終 F+1 是 captured mask 的 set bit；這是充分條件，本機程式沒有檢查此 invariant。一般 fallback 只要 rank 小於 set-bit 數便會命中，直接 bit J 命中則不需要讀 divisor。
- A0 唯一賦值是載入 captured mask，兩個 RET 都回傳 **mask**，不是選中 index 或 success status。

## 對 sampler 的保存證據

完整 leaf 沒有 calls、frame、尾跳或 S／SP／RA 寫入；所有 GPR definitions 僅為 A0..A7。三個 store sites 都是 byte：F+1、C+13、以及條件性的再次 F+1。

這些 nominal 位址與下列來源不重疊：

| sampler／selector 欄位 | 本機 leaf 是否直接寫入 |
|---|---|
| F+26，sampler 的 K byte | 否 |
| `[C+8,C+12)`，sampler baseline word | 否 |
| F+27，proposed step byte | 否 |
| `[F+20,F+24)`，captured mask word | 否 |
| C+17，divisor byte | 否 |

sampler 的 linked call 已接到這個完整 leaf，並於返回後重新讀 F+26 與 C+8。匹配的 leaf 在正常記憶體完成／無 alias 等前提下本機有限，且不改 sampler 保存在 S0／S4 的 q／r。這縮小了先前未知 callee 的 clobber 與 K-writer 缺口。

sampler 本機迴圈的唯一 store 是 C+8 word，內層 leaf 的固定 stores 也排除 F+26。因此在實際 matching code、ordinary accesses、無外部 writer／IRQ／DMA／重入／物理 alias 等條件下，這組本機程式沒有於初始 K snapshot 後直接改寫 K。這仍不證明實際 K>0，也不證明外部狀態穩定。K=0 的外層不進展情況、clock 綁定及整個 attempt 的等待界線仍保留。

## 驗證與剩餘工作

驗證固定完整 operands、unsigned REMU encoding、五處 QingKe byte load/store 標記、三個 stores、GPR clobber envelope、兩個 RET、全部 CFG 邊與不可變 scan witness。拒絕 **62 個逐指令 mutation、2 個 REMU-mode mutation**。

host bitstring 檢查範圍為 65,536 個 `mask=low16|(low16<<16)` family，各搭配 32 個 proposed indices，共 **2,097,152 對**，並檢查 65,536 對 byte proposal 與 8,192 對 J／divisor 算術。這不是全部 32-bit masks 的窮舉；完整 generic 行為仍由原指令／CFG 合約支持。算術使用 set-bit list 與 rank identity，沒有逐指令 scan 或可變目標狀態模型。一般與 `-O` 模式精確重放同一 JSON。

候選 ISA／first-copy／installed leaf、有效 code／global accesses、一般記憶體完成、無破壞性 alias／外部 writers 等仍是前提。下一步需追查 C+17／C+13／F+27／mask F+20 的 writers、K 的來源與約束，以及 `0x6434a/0x64434`、`0x63b0e/0x63bf8` 與 callback 本體；實際 provider、整體 polling 進展與完整指標保存期尚未驗證。

```powershell
python analysis/check_v4160_b1_sampler_inner_static.py
python -O analysis/check_v4160_b1_sampler_inner_static.py
```
