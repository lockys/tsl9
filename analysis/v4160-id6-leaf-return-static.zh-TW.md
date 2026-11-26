# ID6 getter、callback 登記尾跳與下一個 ID7 邊界

接續[完整 ID6 initializer](v4160-outer-id6-initializer-static.zh-TW.md)，本次閉合兩個小型 leaf 的本機合約，並核對返回 outer 後的下一筆 task 登記。這些 resident bytes 仍屬參考候選；實際 RAM provider 綁定與裝置執行結果尚未確定。

| 範圍（右端不含） | V131 | V140 | 每版大小／指令 |
|---|---|---|---|
| fresh count getter | `4efd8..4efe2` | `4f070..4f07a` | 10 B／3 |
| callback 登記 leaf | `4efe2..4f00c` | `4f07a..4f0a4` | 42 B／17 |
| 返回後 outer window | `6dd2e..6dd3e` | `6df1e..6df2e` | 16 B／4 |

新範圍共48條指令，逐一固定 operands、邊界及完整 SHA256。[JSON 證據](v4160-id6-leaf-return-static.json) 包含兩版完整指令、CFG、13種 callback 掃描路徑與256個 getter byte 的算術域。

## Getter：兩次讀值不能自動相等

getter 只 fresh 讀取 unsigned byte `200033b4`／`20003404`，放入 A0 後 RET。它沒有 store、frame 或 call，僅改寫 A0/A5；本機不改寫 SP、RA、GP、S registers。

parent 在兩個呼叫點讀取它；中間有 allocator 呼叫。令第一次值為 g1，第二次為 g2：

```text
allocation request = (12*g1) & 65535 = 12*g1
fill request length = 12*g2
g1, g2 ∈ 0..255
```

因此兩個長度各為0..3060 bytes，low16 在這個 unsigned-byte 域內不截斷。不能由此推得 g1=g2，或 fill 一定落在有效 allocation extent。若 count 保存為前階段 q，才可收緊為0..66；APP source byte14 的條件性來源案例給 q=5，兩個長度都為60 bytes，但仍要求跨呼叫保存。

## Callback table：12個 fresh 讀取與兩種返回

leaf 操作固定48-byte表：V131 `20003358..20003388`，V140 `200033a8..200033d8`。初始化 index=0、scan pointer=table base；每次 LW 一個 word。

- 遇到第一個讀得零的槽位：計算 base+4*index，將**入口 A0** SW 到該槽，然後返回 A0=0、A1=0、A2=12。
- 12次讀取都非零：不寫表，返回 A0=19、A1=第12槽當次讀得的非零 word、A2=12。

它沒有 call 或 frame，僅定義 A0–A5；不改寫 RA、SP、GP 或 S registers。本機唯一 store 直接保存入口指標，沒有呼叫該 callback，也沒有重複指標或 null 檢查。若傳入零，該 store 仍會寫零並返回成功；本次 parent 的條件性入口指標則是非零 `4d916`／`4d9ae`。

檢查器建立首個零位於 slot0..11，以及全12槽非零的13張有限 CFG 路徑憑證，兩版共26張。每張都核對邊相接、終點 RET、讀寫次數及 cursor/index 關係；最多12次讀取。這是原指令的有限控制流證據，沒有建立或執行目標 table／register 狀態模型。

各槽是分別 fresh 讀取，不能把結果當成一致快照，也不能推定發布具原子性、callback 物件仍有效或其他 writer 不會改表。正常返回要求有效 code/table 存取，以及表與 caller frame/code 沒有實體 alias 等條件。

## 清零的來源條件

上一階段非零 resource 路徑的尾跳 fill 正好要求清零這48 bytes。若該 fill 實際完成，且零結果保存到這個 leaf 的 fresh read，會在 slot0 寫入 `4d916`／`4d9ae`，返回 `(A0,A1,A2)=(0,0,12)`。

此條件不能省略：resource count=0 路徑不執行該 fill；其後 parent 還有 allocator、fill 與動態 payload stores，保存效果未閉合。parent 最前面的另一個48-byte fill 與 callback table 分離，不能拿來證明此表已清零。pool pointer word 緊鄰表前，但不包含在表內。

固定 callback table 各槽與 task count/capacity/table-pointer、task table T、相關 config 欄位及 getter count byte 的地址區間分離。這只排除已列固定寫入的直接重疊；未知 provider、動態 payload、非同步 writer 與實體 alias 仍需另證。

## 尾跳返回與下一個 initializer

parent 在尾段取回 saved RA，釋放48-byte frame，再帶 A0=`4d916`／`4d9ae`，以不設 link 的跳躍進入 callback 登記 leaf。若 parent 確實到達這裡、frame/RA 等保存前提成立，leaf 的 RET 便回到 outer `6dd2e`／`6df1e`。這個連結不等於已證明整個 parent 必然完成。

outer 沒有測試 callback 登記的0或19返回值，直接將 A0 改為下一個 task handler `465b4`／`4664c`，呼叫 task-registration `43c4e`／`43cda`。

若此時 fresh task count仍7、capacity仍≥14、table pointer仍為 T=`200047f4`，且 extent／非alias／保存前提成立，該登記會將 handler 寫入 entry7=`20004810`，回覆 A0=7、A2=8，count變為8。task-registration 本機不定義 A1，因此它保留 callback 登記 leaf 的 A1：

| Callback 登記情況 | 下一個 initializer 的 A0 | A1 | A2 |
|---|---:|---|---:|
| 找到零槽並寫入 | 7 | 0 | 8 |
| 全12次讀取非零 | 7 | 第12槽當次讀得的非零 word | 8 |

所以先前 initializer 入口的 A1=`ffffffff` 已被這個 leaf 的 LW 改寫，不能繼續沿用。新的分析邊界停在 `6dd3a`／`6df2a` 對 `46570`／`46608` 的呼叫前；尚未證明下一個 initializer 的副作用或返回。

## 重播

[靜態檢查器](check_v4160_id6_leaf_return_static.py) 只讀取離線原始 bytes，沿用既有完整 initializer／resource／registration 合約與輸入身分檢查。

```text
python analysis/check_v4160_id6_leaf_return_static.py
python -O analysis/check_v4160_id6_leaf_return_static.py
```

兩種模式均要求精確 JSON 重播、48次逐指令 operand 變異拒絕、26張 CFG 路徑憑證與256個 byte 算術域。未執行或模擬目標 ISA、callback、allocator、fill、MMIO、CSR 或 trap。新增靜態證據不增加既有 C 重建進度，該基準仍約88.09%。
