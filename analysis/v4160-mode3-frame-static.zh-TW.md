# v4.1.60：完整mode 3 callee的frame與寫入範圍

本輪補齊APP `0x1929a..0x196c4` 的完整本機控制流、記憶體基址來源與frame合約。原始本體共1,066 bytes／329條指令，50個store全部分類為本函式frame內寫入或固定MMIO寫入。唯一callee是既有完整驗證的reader `0x191c6`，有六個呼叫點。

接續 [前12個config call sites](v4160-config-precallees-static.zh-TW.md) 與 [APP config建立來源](v4160-app-config-source-static.zh-TW.md)，現在可在正常返回、有效存取、無不利別名／外部干擾等前提下，將constructor初始config保存結論帶過第13個前置呼叫，直到APP呼叫fresh `[0x40074]`。這仍不跨越provider的optional hook，也不證明實機輪詢終止或installed provider身分。

全程只做bytes、CFG、反向定義來源與整數／區間代數檢查。未執行或模擬目標ISA、signed division、MMIO、輪詢、RAM/frame或裝置。C重建覆蓋率未增加。

## 證據與範圍

程式：[check_v4160_mode3_frame_static.py](check_v4160_mode3_frame_static.py)。證據：[v4160-mode3-frame-static.json](v4160-mode3-frame-static.json)。來源APP與既有candidate／sparse HEX／SDK／Xwchc驗證鏈保持固定身分。

```text
完整範圍（右端不含）：0x1929a..0x196c4
SHA-256：0b79dfccf11a0f49b7d234d0efdd318c2d564ff95e4d8711c12aee0fb963a236
原始大小：1066 bytes／329 instructions
memory accesses：119
stores：50
```

不能停在`0x196ba`的RET：其後兩段signed-rounding修正仍有本機分支可達。完整CFG無cuts，所有329個節點均由本機入口條件性可達，唯一terminal是該RET。每個call只加入正常返回時的續行邊，不代表它必定返回。

本輪獨立釘住所有store、控制邊、frame欄位、位址來源及新增signed DIV／C.SRAI解碼；其他算術指令保留完整原bytes及decoded operands，尚未逐式建立整個演算法或物理單位的語意。

## mode 3如何進入與返回

constructor `0x19ba8` 以JAL呼叫`0x197b8`，link為`0x19bac`；小wrapper設A0=3，再以JAL X0尾跳`0x1929a`，不建立新link。完整callee若在frame／context有效等前提下普通RET，就返回constructor的19bac。

callee先fresh讀一次`U32[entry GP+108]`，之後用在signed DIV及其他算術。沒有確認該word的實際值、來源writer或物理含義。入口A0在無本機改寫下存入S1；六個reader呼叫不改S1，因此`0x19556`的OR仍使用mode值3。這只界定寄存器operand，不保證後續硬體欄位值。

## 所有記憶體基址的靜態證明

驗證器對119個memory accesses，沿CFG反向收集base register的may-reaching definitions，跨過分支、loops與reader的實際GPR clobber集合。每一處都必須得到唯一來源，再核對其固定LUI／ADDI或frame／GP來源。這是有限圖上的定義來源分析，不是逐PC執行register machine。

非stack來源只有：

- 入口`GP+108`的一次word讀取，沒有GP-relative store。
- 13個明確的LUI roots=`0x40022000`。
- 兩個derived A5 roots：`0x1945a`、`0x19596`各加44，得到`0x4002202c`。

因此`0x1948a/0x19496/0x195c6/0x195d2`的`SH [A5+32]`均是`0x4002204c`。中途A3已改成mask常數，不能再把then-live A3視作這些store的base。

36個非stack store instructions只有四種有效地址／寬度：

| encoded有效地址 | 寬度 |
|---|---|
| `0x40022049` | byte |
| `0x4002204f` | byte |
| `0x4002204c` | halfword |
| `0x40022036` | halfword |

另外會讀byte `0x4002204e`；沒有其他variable-input-pointer store。每個load還分別核對unsigned byte／halfword或word encoding。這些位址與順序不賦予硬體校準、同步、狀態提交或復原成功的含義。

## 80-byte子frame與caller config分離

設此callee入口SP=C。入口SP−=80，保存RA和S0..S11共13個word，位於`C−52..C−1`；另有一個scratch word位於`C−68..C−65`。這14個stack store instructions都在自己的80-byte frame內，與constructor的config `[C,C+16)`、保存RA `[C+28,C+32)`不重疊。

所有restore都由對應save支配；每一條到RET的本機路徑都經過RA／S0..S11 restore，且它們是返回前對應GPR的最後定義。SP僅有入口−80及尾端+80兩個定義；GP未被定義。恢復S registers後的尾端算術／MMIO仍在完整範圍中，沒有略過。

六個call sites全部指向`0x191c6`：

```text
19382,1938a,1949a,194a0,195d6,195dc
```

重播既有reader的完整90-byte原本體可確認：沒有store、frame或nested call，只定義A0..A5，因此不直接改SP／RA／S／GP。實際memory／MMIO side effects、physical aliases、DMA、interrupt、reentry及外部writers仍須排除，才能把本機寫入分類轉成caller frame保存結論。

## 輪詢與外層上限不能混為一談

完整conditional-normal-return CFG有九個cyclic SCC：

| SCC首尾PC | 節點數 |
|---|---:|
| `19316..19404` | 71 |
| `19456..19462` | 5 |
| `194a0..194a4` | 2 |
| `194bc..194c4` | 4 |
| `194cc..194d4` | 4 |
| `19592..1959e` | 5 |
| `195dc..195e0` | 2 |
| `195f8..19600` | 4 |
| `19608..19610` | 4 |

第一個大SCC包含外層修正、MMIO polling及scratch保存的reader reply等待。其餘有fresh bit15 polls與reader reply相等時的等待；`SLLI16; SRAI16`後的signed比較精確測halfword的bit15。reader自身也有四個重讀迴圈。

S10在外層入口前設4；每次retry至19316都必須經過減1、AND255與zero-exit guard，且reader不改S10。所以在內層poll／reader會前進、無外部干擾的前提下，這個外層最多4 passes／3條retry edges。這不限制單次內層等待多久，亦不建立整個函式eventual return。

向低PC的signed-rounding匯流jump已按CFG處理，不直接當作額外迴圈。16條signed DIV只解碼並保留operands；未用Python／C除法替代目標的zero-divisor、overflow或signed-rounding語意，也未宣稱算術結果或物理校準已驗證。

## config保存結論的邊界

若前12個callee合約成立，本輪第13個mode3 callee及其reader都正常返回，且code／frame／MMIO存取有效、沒有不利physical alias／外部干擾，則constructor的16-byte初始zero區、RA／SP及所需S／GP可帶回19bac。之後APP重寫config words0／4／8而不改byte12..15，因此零值可以條件性帶到fresh40074呼叫。

這不證明`[40074]`在實機綁定哪個provider。provider的optional hook仍可能改動frame、saved pointer或source bytes；跨hook的gates、copy／publication、payload與指標保存期仍須另外確認。

## 重播與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_mode3_frame_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_mode3_frame_static.py
```

檢查涵蓋完整byte identity／329-node CFG、50個store、119個memory基址證明、六個reader接點、九個SCC、13個saved fields的支配與最後定義、65,536種halfword sign-bit等式、frame區間與外層ranking，以及138個指定operand變異拒絕。JSON必須逐bytes重播一致。

後續仍需追查實際provider／slot writers與optional hook／registration副作用、`GP+108`來源及signed算術合約、MMIO進度／外部writers與保存期，以及其他算術helper實參域。
