# v4.1.60：完整 NV read wrapper 與 B1 buffer 合約

本階段核對 `440c2..44310`／`44156..443a4` 的完整 read wrapper，每份 **590 bytes／202 instructions**，兩份合計 **1,180 bytes／404 instructions**。兩份 body 均逐 byte 比對原始 sparse HEX，並接上既有 B1 selector、updater 與 optional output 的實際呼叫位置。

[檢查器](check_v4160_b1_nv_read_static.py) 與[確定性帳本](v4160-b1-nv-read-static.json) 保存完整 operands、SHA-256、CFG、分支及兩個掃描迴圈的語法見證。沒有執行或模擬目標指令、callbacks、NV provider、RAM service 或硬體；沒有建立可變的目標記憶體／queue 模型。

## 三組參數的意義分開

入口將 `(ID,L,O)` 保存至 S4／S1／S2。wrapper 內的三個數值不能混為同一個長度：

| 位置 | 原指令傳遞的數值 | 可證明範圍 |
| --- | --- | --- |
| 配置請求 | fresh U16[F+12] | allocator 的數值大小參數 |
| 設定 read callback | fresh U16[F+12] >> 2 | callback 第二參數；實際單位與輸出 extent 未知 |
| 命中後的 copy | 原始完整 L | 原樣傳給 `20000332(O,H+4,L)` |

串接[既有 copy leaf](v4160-b1-selector-transform-static.zh-TW.md) 後，matching candidate copy 以 byte 為迴圈單位。因而 B1 的 L=16／64 對應 copy 請求的 16／64 bytes；**這不等於證明 NV callback 寫入了同樣長度，或 O 已收到有效資料**。實際 RAM 綁定、code copy、有效範圍及物理效果仍為條件。

F 是設定物件，C 是共用 context：

| 欄位 | V131 | V140 |
| --- | --- | --- |
| F base | `200031ec` | `2000323c` |
| C base | `2000319c` | `200031ec` |
| buffer word C+32 | `200031bc` | `2000320c` |
| owner word C+36 | `200031c0` | `20003210` |

第一次讀到的 F+8 為零時走 RAM 路徑；非零時先要求當次 F+56 非零。後續三個 indirect call sites 會**重新讀取 F+56，沒有第二次 null guard**；不能把初始 guard 當成對較晚 callback 的綁定證明。

## B1 使用的 configured 高 ID 路徑

在 F+8 非零且初始 callback guard 通過時：

| 完整 unsigned ID | 計算 page 的 index |
| --- | --- |
| `512..0x6fff` | signed truncation `(ID-512)/6`；此域內被除數非負 |
| `0x7000..0x7ffe` | `ID-0x7000` |
| 更高 | 返回 10 |

`page = captured_F8 + index * fresh_U16[F+12] mod 2^32`。B1 的獲准 i 最大為 254，所以：

- `512+6*i` 與 `515+6*i` 都選到 page index i，但保留兩個不同的完整 ID 作為後續列 key。
- `0x7000+i` 走另一組 page index i。
- NV wrapper 沒有因 `515` 與 `512` 的差額直接對來源加 3；先前 selector 的 caller-side scratch 切片是另一件事。

若 C+36 等於 page，且 fresh C+32 非零，取該 pointer 為 P；否則請求 `allocate(fresh_U16[F+12],78)`，null 返回 10。配置成功後請求：

```text
fresh_F56(page, fresh_U16[F+12] >> 2, P)
```

Callback 返回值不檢查。高 ID 路徑本身**不發布新 P 至 C+32／C+36**。配置時的 size 與 callback 時的 size 是不同次 fresh load，不能假定相等或據此證明 buffer 足夠。

## 列查找使用固定 base 的絕對位移

第一個 header H=P+4，依序讀取：

1. U8[H+2] marker，不等於 `0x5a` 即失敗。
2. U16[H+0] key，與原始完整 ID 比較。
3. key 不同才 fresh 讀取 U8[H+3] 的 q；下一個 header 是 **P+(q & 252)**。

下個位置以固定 P 為基準，不是從目前 H 再往前走。q 的 256 個值只有 64 個對齊後位移；例如 q=4..7 都回到 P+4。原指令沒有 visited-set、迭代上限、size 邊界或進展檢查；因此不能證明終止。這是地址算式與 CFG 的限制，沒有模擬一份記憶體或宣稱真實資料必然造成迴圈。

命中時請求 `copy(O,H+4,L)`，忽略其返回值。之後 fresh 讀 C+32 與捕獲的 P 比較：相等就不釋放，不等就請求 private release `20000110(P)`；正常返回後強制狀態 0。marker 失敗也做相同 pointer 比較與條件性 release，但最後強制返回 10。

這是 pointer equality 決策，不是配置來源或 ownership 證明。C+32 可在 callback／copy 期間改變；配置出的 pointer 不一定與較晚 C+32 相同。wrapper 的 0 也不證明初始化、實際 copy 完成、有效 nonnull O 或資料保存。匹配的 copy 遇 null 會跳過 payload transfer；其返回值被這個 wrapper 忽略，後者仍可返回零，不能把它解讀為 copy 自身回報成功。

## F+8 為零的 RAM 路徑

此路徑直接 fresh 讀 C+32 為 P：null 返回 10；其餘使用相同 marker／U16 key／絕對 U8 位移掃描，命中後 copy 並返回 0，marker 失敗返回 10。

這條路徑不配置、不經 F+56 callback，也沒有 private release。它同樣適用於 B1，不受前述 configured page ID 區間控制。不能從 F+8=0 推得內容清零；與[既有零基址列讀取](v4160-base-zero-row-read.zh-TW.md)及[cache 生命週期](v4160-zero-base-cache-lifecycle.zh-TW.md)的結論一致，現已補上兩候選的完整 wrapper 驗證。

## Configured 低 ID 路徑也已完整覆蓋

ID<=511 先取得 C+32。若 null，請求 `allocate(fresh_U16[F+12],0x4e01)`，**先將結果發布到 C+32，再判斷 null**。成功後 callback 使用 fresh F+8、fresh size>>2 與當時配置 pointer；之後重新讀 C+32 作為 local P，再把 fresh F+8 寫至 C+36。

若原本 C+32 非零且 owner C+36 等於最初捕獲 F+8，直接重用；owner 不同則以 tag `0x4e02` 配置 temporary，callback 後不發布 temporary。

| 特殊 ID | L guard | 相對 P 的 header offset |
| --- | --- | --- |
| 2 | L=16 | `4*trunc_signed((fresh_U16[F+12]-64)/4)` |
| 3 | L=16 | `(fresh_U16[F+12]-44) & ~3` |
| 4 | L=4 | `(fresh_U16[F+12]-24) & ~3` |
| 256 | L<=8 | `(fresh_U16[F+12]-16) & ~3` |

其他低 ID 或錯誤 L 返回 10，但在此之前仍可能已配置或呼叫 callback，不能概括為「拒絕參數就沒有副作用」。特別是 ID2 的除法為 signed、朝零截斷；size<64 時不能以 unsigned 除法替代。這些 offset 計算沒有提供 size 下界或完整 payload extent 的保證。

特殊 header 也需 marker 與 key 同時匹配才 copy。Copy 或 header 檢查後，依 fresh C+32 與 local P 的相等性決定是否 private release，再返回固定 0／10。

## Pointer 保存期與後續缺口

這個 wrapper 的本機 stores 僅有 8 個 frame words 與低 ID 路徑的 C+32／C+36 兩次發布；原始 O 保留在 S2，交給 copy，沒有直接寫成 global pointer。Callback 的明確 A2 是 heap／cache P，不是 O。這些局部事實不能排除 ambient registers、alias、callee 副作用或其他 writers 保存 caller pointer。

仍需驗證完整 write wrapper `4435c / 443f0`、未知 worker `51f78 / 52020`、其 core，以及實際 F+56／F+60 綁定、設定／context writers 與完整物件保存期。當前不宣稱 NV 寫入、硬體存取或實機韌體功能已重現；C 重建覆蓋率也沒有因新增分析帳本而增加。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_nv_read_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_nv_read_static.py
```

檢查固定兩份 body 的全部 operands，拒絕 404 個逐指令 mutations 與 48 個 typed-load mutations；驗證 32,255 個 configured 高 ID、255 組 B1 index joins、完整 U16 callback-count／signed-DIV scalar domain 與 256 個 U8 位移。一般及 `-O` 模式逐 byte 重播相同 JSON；所有 paths 為不可變 CFG 見證，語法可達不代表實際輸入或 provider 執行可達。
