# v4.1.60：generator 完整本體、重試界限與 fallback

本階段完整核對 `640d8..641b0`／`641c2..6429a`，各 **216 bytes／73 instructions**，合計新增 **432 bytes** 原始指令證據。既有 callback、byte／U16 range wrappers 及 word source 只重用，不增加既有 C 重建覆蓋率。

兩版 SHA-256 分別為：

```text
V1.31 550457058926bad27d26b639e435ee11b2716f53af68d0080ea9416e85d9bcde
V1.40 f4b8c265605c98c6788a60a1c2c148f4554ad0d717b2e032073297a925d7722b
```

[完整 ledger](v4160-generator-static.json) 保留全部 literal operands、完整 CFG、calls／stores、路徑、迴圈界線與整數證據。全程僅讀取原 bytes、解碼、處理圖及主機端 bitstring／scalar arithmetic，沒有執行或模擬目標 ISA、RNG、provider、callback、MMIO、裝置或 mutable register／RAM machine。

## 入口與呼叫鏈

generator 不使用入口 A0 作 seed；它在任何 A0 讀取前先覆寫 A0。frame32 保存 RA、S0～S4，六個 stores 全部位於自己的 frame，沒有直接 global 或 N′ 存取。

沿用 [N+136 callback 證據](v4160-n136-predicate-static.zh-TW.md)，callback 在 `+ce` 呼叫 generator，於 `+d2` 把實際完整 A0 回覆存入先前捕捉的 N′+88。這個保存動作不保證 N′ 仍有效、callback 真正綁定或 caller／callee 之間物件身分保持。

兩個靜態 callee sites 為：

| 用途 | V1.31／V1.40 target | 參數 |
|---|---|---|
| main candidate | `43e8e/43f1a` U16 wrapper | `(0,65535)` |
| fallback | `43e6a/43ef6` byte wrapper | `(16,240)` |

匹配既有 wrappers、普通 MULHSU／整數語義及必要 source／frame／S-register 保存前提下，前者回覆 q∈**0..65534**，後者回覆 r∈**16..239**。兩個上界都不包含第二參數；沒有假定來源均勻、隨機、互相獨立或每個代數值在實機可達。

## Main candidate 的固定結構與篩選

候選字由 U16 回覆 q 形成：

```text
q bit0 = 0 : word = (q << 8) OR 6a0000e6
q bit0 = 1 : word = (q << 8) OR ac0000ce
```

接著依序檢查：

1. **環狀相鄰位元轉換**最多 24 次，超過就重試。第一段 index0..31 比較 bit k 與 bit((k+1)&31)。RV32 register SRL 只採 shift amount 低五位，最後的 shift32 是 shift0，因此比較 bit31 與 bit0。transition counter 最大32，AND255 在這個範圍不會 wrap。
2. 檢查 **27 個線性六位元視窗**，shift0..26；任何視窗為 `000000` 或 `111111` 就重試。這不是環狀視窗掃描。
3. 四個 bytes 全部相同才重試；否則直接恢復 frame 並返回候選字。對目前固定 candidate family，最高／最低 byte 已經不同，因此這個最後 rejection 分支在 helper-domain 前提下不會選中。

第一段環狀 shift 的語義需與一般 Python `word >> 32` 區分。純 bitstring 例子 `80000001` 的環狀 transition count 為2，若誤把最後一步右移32視為補零，會算成3。當前 candidate family 的 bit0 固定為0，這個特定差異並不改變其最後一次比較，但原指令仍必須保留正確 SRL 語義。

## 65,535 個候選字的整數域核對

在 q=0..65534 的純代數域，依原分支優先序分類如下；這不是 RNG 或目標函式執行。

| 分類 | 個數 |
|---|---:|
| transition count >24 | 1 |
| 通過 transition、六位元視窗不合格 | 16,344 |
| 四個 bytes 相同 | 0 |
| 通過 main filters | 49,190 |
| 合計 | 65,535 |

唯一 transition rejection 為 q=`aaaa`、word=`6aaaaae6`，環狀轉換26次。第一個通過候選為 q=`0820`、word=`6a0820e6`，轉換14次且沒有禁用視窗。

checker 逐一核對 circular-popcount 公式與32個 bit-pair 比較公式一致，並固定完整 transition histogram 及通過字序列的 SHA-256。這些數量描述代數域，不是實機成功率、機率、實際來源序列或 ingress 可達性。

## 255 次 main 嘗試後進入 fallback

retry counter S0 初值為1。每次 candidate rejection 都執行 S0+1 並 AND255；只要非零，就產生下一個 main candidate。非零值序列恰為1..255，第255次 rejection 後為0，下一輪選 fallback。

因此在各次 callee 正常返回並保存 generator 的 live S registers、frame／SP、返回位址，以及 ordinary RV32 指令／存取語義前提下：

- main requests 最多255次。
- 每次 main attempt 最多32次 transition iterations、27次 window iterations，可提早拒絕。
- fallback request 最多1次；range-helper requests 合計最多256次。

局部圖有 retry／scan cycles；checker 分別移除 `+8c→+70`、`+a8→+98`、`+d6→+28` 三條有界 backedges 後，剩下的圖無環，並核對各 counter 的初始化、步進、mask 及停止常數。

這不是整條呼叫鏈或實際時間的完成保證。range helpers 會呼叫 stateful word source，後者包含控制欄位操作、狀態寫入及 optional callback；未知 installed callback 可能不返回或破壞上述保存條件。

## Fallback 返回值不保證通過 main filters

fallback 請求 byte wrapper `(16,240)`，回覆 r 後立即形成：

```text
fallback word = (r << 16) OR 6a00ace6
```

接著直接進共用 frame restoration／RET，**不經 main filters**。

在224個 r=16..239 的代數值中，212個恰巧通過 main filters，**12個不通過六位元視窗條件**。對應 r 為：

```text
31 63 64 95 126 127 128 129 159 191 192 223
```

例如 r=31 形成 `6a1face6`，shift15 的六位元視窗為六個1，但 fallback 仍直接返回。這是 formula witness，沒有宣稱實際 source 必定提供31或已觀察到該執行路徑。

主路徑49,190個通過字與224個 fallback 字重疊212個；聯集為49,202個代數返回字。因此「generator 所有返回值均通過 main filters」不成立；不能為重建版本增加這個更強的保證，也不能自行把 fallback 再過濾。

## 重播與後續邊界

[Checker](check_v4160_generator_static.py) 驗證146次 instruction mutations、22條選定 CFG walks、166條 edge witnesses、65,535個主候選與224個 fallback 值、255-retry bound，以及 callback／helper 的原指令串接。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_generator_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_generator_static.py
```

一般／`-O` 模式都必須精確重播相同 ledger；guards 不依賴 Python assert。matching byte wrapper 的既有參數／MULHSU 證據見 [尾段 wrappers](v4160-comparator-tail-static.zh-TW.md)。

仍需將既有 timer／lookup／算術 helper 證據串成更完整的返回與保存合約，並追查實際 provider／source 綁定、global／callback writers、物件及借用 pointer 生命週期、alias 與硬體效果。
