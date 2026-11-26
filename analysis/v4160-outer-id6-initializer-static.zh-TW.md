# 第一個外層 ID6 initializer：完整指令與資源數量邊界

接續[返回發布與 clock 來源](v4160-gate-return-publication-static.zh-TW.md)，本次完整展開 V131 `4da70`／V140 `4db08`，以及它們第一個直接 callee `4edd2`／`4ee6a`。這些 resident 映像仍是參考候選，不能據此宣稱 v4.1.60 裝置已安裝相同 provider。

| 範圍（右端不含） | V131 | V140 | 每版大小／指令 |
|---|---|---|---|
| 外層 initializer | `4da70..4dbf2` | `4db08..4dc8a` | 386 B／123 |
| 第一個資源 callee | `4edd2..4ee72` | `4ee6a..4ef0a` | 160 B／55 |

兩版合計 356 條指令逐一驗證 opcode、暫存器、位移、分支目標與邊界，另固定完整 bytes 的 SHA256；完整值、CFG 與呼叫清單保存在 [JSON 證據](v4160-outer-id6-initializer-static.json)。CFG 的 call fallthrough 表示「callee 正常返回」的前提，不代表已證明實際返回。

## ID6 的來源與 frame

沿用前一階段條件性路徑，進入 initializer 的 A0=6、A1=`ffffffff`、A2=7，前次登記後 task count=7。initializer 使用 48-byte frame，保存 RA、S0–S4，並額外將完整 A0 存於 SP+12。以 initializer 入口 SP 為基準，saved ID 位於 −36；第一 callee 的 16-byte frame 位於 −64，其 saved RA 位於 −52，兩者分離。

第一 callee 正常返回後，initializer 重新 LW saved A0，將低 byte 發布到 `20003314`／`20003364`。因此這裡的 ID6 來自保存的入口參數，不依賴 callee 返回的 A0。此結論仍要求 frame、SP、相關暫存器和記憶體存取有效。

callee 之前有九筆固定狀態寫入；檢查器逐一確認其地址與 task metadata、table、相關設定來源欄位分離。這只證明固定寫入的區間關係；後續動態 allocator／fill、payload、heap metadata 與非同步寫入的保存效果仍待證明。

## 資源數量另讀 config byte

第一 callee fresh 讀取設定 F+21：V131 `20003201`，V140 `20003251`。令該 unsigned byte 為 b：

```text
r = b & 3
q = r + (b >> 2)
```

它將 r 寫到 `200033b5`／`20003405`，q 寫到 `200033b4`／`20003404`。完整列舉 256 個 byte 值，得到 q=0..66，且 q=0 當且僅當 b=0。這個數量與 task ID6 是不同來源。

- **b=0：**直接恢復 frame 並 RET；不呼叫 allocator 或 fill，也不清除先前 pool pointer／callback table。接回 saved ID6 的載入及發布，下一個邊界為 parent 的 fill 請求 `(20003320/20003370, 0, 48)`。其右端恰為 `20003350/200033a0`，不包含下一個 fresh count byte。本次停在這個 fill 呼叫前。
- **b≠0：**第一個邊界是 RAM `20000040` 的 allocator 請求 `(60*q, 9001)`，request 範圍 60..3960 bytes。本次不跨過該呼叫宣稱 payload 或 metadata 已保存。

APP builder 的 packed halfword `0e3f` 位於設定 field20，因此 source field21=14。既有 config defaults 的固定寫入不覆蓋 field21；若來源 frame、matching 64-byte copy、驗證及 fresh 設定保存等條件均成立，這個來源案例會得到 **q=5、request=300 bytes**。這不等於已證明當前設定值，也不能把 b=0 的可閉合分支當成實際預設路徑。

## 非零路徑的完整靜態形狀

完整 body 顯示 allocator 返回 pointer 寫入 `20003354`／`200033a4`，接著請求 fill；其長度使用再次 fresh 讀取的 q byte 乘60。這裡沒有 allocator 返回值的本機 null guard。

fill 後又 fresh 讀取 count，逐筆記錄以60 bytes為步長，寫入 halfword+2=`ffff`、byte+4=0、word+44=0。迴圈界已載入 unsigned byte 暫存器，因此在存取與 GPR 有效的條件下，最多255筆；只有 count 保存為原 q 時，才能收緊為最多66筆。完成後釋放 callee frame，尾跳 fill `(20003358/200033a8, 0, 48)`。

這些是原指令所要求的資料流；有效且不 alias 的 payload extent、allocation 成功、fresh count 與配置長度的關係、RAM provider 綁定、fill 結果及所有跨呼叫保存條件都未由此自動成立。本次沒有構造輸入、測試裝置或觸發這些路徑。

## Parent 後段與下一步

完整 initializer 有10個 linked calls、1個尾跳、26個 store、15個 load。除了第一 callee，還有三次 allocator、四次 fill，以及兩次 getter。三個 allocator tag 依序為 `4c04`、`4c05`、`4c06`。所有 AUIPC/JALR 的靜態目標均逐對核對。

本機16-byte記錄迴圈只寫 byte+9=`ff`；index 每次加1後 mask255，再與已讀入的 unsigned byte count 比較。數學域檢查涵蓋0..255，最大255次；有效 payload 及保存前提仍需要另外證明。

parent 最後恢復 frame，帶 A0=`4d916`／`4d9ae`，尾跳 `4efe2`／`4f07a`。它本身沒有 ordinary RET，因此本次尚未固定後續 outer task IDs。下一步可展開 getter `4efd8`／`4f070` 與此尾跳函式，再釐清配置、清零及 callback table 保存條件。

## 重播

[靜態檢查器](check_v4160_outer_id6_initializer_static.py) 只解析與驗證離線 bytes，不執行或模擬目標指令、allocator、fill、callback、MMIO、CSR 或 trap。

```text
python analysis/check_v4160_outer_id6_initializer_static.py
python -O analysis/check_v4160_outer_id6_initializer_static.py
```

驗證包括356次逐指令 operand 變異拒絕、256個來源 byte、兩版完整 CFG／frame／呼叫清單，以及精確 JSON 重播。既有 APP、candidate、SDK、來源與上游靜態證據身分檢查一併重播。本次新增的是靜態合約證據，既有 C 重建進度約88.09%維持不變。
