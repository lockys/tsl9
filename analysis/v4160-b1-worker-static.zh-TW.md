# v4.1.60：worker、倒序 copy 與固定零返回的 core 外層

本階段把[既有 V131 工作區摘要](v4160-link-type3-workspace.zh-TW.md)延伸為兩個候選的完整 body、原始 sparse HEX 與可重播驗證，共 **500 bytes／182 instructions**。沿用的 fill leaf 另計 92 bytes，不重複納入本階段 body 總量；這也沒有增加 C 重建覆蓋率。

| Body | V131 | V140 | 每份 bytes／instructions |
| --- | --- | --- | --- |
| worker | `51f78..52008` | `52020..520b0` | 144／52 |
| 倒序 copy 的 linked RAM entry | `2000048a..200004bc` | 相同 | 50／16 |
| 倒序 copy 的 FLASH source | `406fa..4072c` | `4073a..4076c` | 已包含上列，不重計 |
| core 外層 | `63890..638c8` | `6397a..639b2` | 56／23 |

[檢查器](check_v4160_b1_worker_static.py)與[帳本](v4160-b1-worker-static.json)固定所有 operands、SHA-256、CFG、分支／迴圈路徑、Xwchc 編碼及呼叫目標。沒有執行或模擬目標指令、provider、core 服務或硬體，也沒有建立可變寄存器、heap 或 RAM 模型。

## Worker：輸出嘗試在釋放之前，返回保存的 core 狀態

以 `(P,V,O)` 表示 worker 的三個入口參數。它保存三者至 S3／S1／S2，請求 `allocate(48,83)`。配置返回 null 時返回 19，不走 fill、copy、core、輸出或釋放。

非零配置 W 的完整順序為：

1. `fill(W,0,48)`。
2. `reverse(W,P,16)`。
3. `reverse(W+29,V,3)`。
4. `core(W,W+16,W+32)`，將完整返回 R 保存至 S1。
5. `reverse(O,W+45,3)`，**沒有先檢查 R**。
6. 請求 `20000110(W)` private release。
7. 返回保存的 R，忽略 copy 與 release 的返回值。

本機五個直接 stores 全部是 frame saves。輸入／輸出的資料搬移與釋放仍是子函式請求，不能只憑這個順序宣稱配置有效、輸出完成、真正釋放或 borrowed pointer 未被保存。

## 2000048a 是倒序 byte copy，沒有 null guard

這個 leaf 與已核對的正向 copy `20000332` 不同。入口 `(D,S,n)` 先捕獲 word `4002420c`、寫零並經 `FENCE.I`，之後才判斷長度；沒有 frame、child call 或 pointer-null guard。

它先算出 source cursor=`S+n-1`、end=`D+n mod 2^32`。每個 payload step：

```text
source cursor 減一
讀 U8[source cursor+1]
destination cursor 加一
SB 至 destination cursor-1
```

在有效、分離且沒有不利並行變動的範圍前提下，第 j 次把來源相對位移 `n-1-j` 的 fresh byte 寫至目的相對位移 j。n=0 不讀寫 payload，但仍經控制字與 FENCE 路徑。正常出口恢復捕獲的控制字，A0=`D+n`、A1=`S-1`、A2=`D+n`；不是回傳原始 D，也不是 snapshot 或 memmove 合約。

`9c31` 依 Xwchc 固定解為 `qk.c.lbu a5,1(a1)`。若把它當一般浮點載入，或漏掉讀取前的 decrement，會把此處的 byte order 判錯。控制字、FENCE、實際存取是否有效與 installed RAM binding 都未執行驗證。

## 48-byte 工作區的可證明切片

在匹配的 fill／reverse helpers 完整正常返回、有效 nonalias 工作區與穩定來源等前提下，core 呼叫之前：

| 相對 W 的 interval，結尾不含 | 本機請求所建立的內容 |
| --- | --- |
| `[0,16)` | P 的 16 bytes 倒序 |
| `[16,29)` | fill 後未被兩次輸入 copy 改寫的 13 bytes |
| `[29,32)` | V 的 3 bytes 倒序 |
| `[32,48)` | fill 後未被兩次輸入 copy 改寫；之後交給 core |

Core 收到三個各 16-byte 的相鄰切片：W、W+16、W+32。輸出 copy 要讀的是 `[W+45,W+48)`，正常資料搬移的 index 算式為 `O[j] <- fresh W[47-j]`，j=0..2。這只界定來源位置與順序；core 是否產生有效輸出、或內層服務是否改寫這三個 bytes，仍未證明。

## Core 外層正常返回固定零，不傳遞服務的狀態

兩份 body 的 global context pointer 分別取自 `2000353c / 2000358c`，沒有 null guard。以 B 表示捕獲的 pointer：fresh 載入 word B+80，OR `0x80`，再 SW 回 B+80。這是 callee 之前的直接副作用；實際 B 指向何物、是否為硬體以及與工作區是否分離，都需要額外證據。

接著：

1. 呼叫 `63eda / 63fc4`，明確 A0=13。當時 A1／A2 仍帶著工作區切片，不能假定第一個 helper 看不到它們。
2. 從 S0 與自己的 frame 恢復原始 A0／A1／A2，呼叫 RAM service `200022be / 2000230a`。
3. 不採用這兩個服務的 scalar reply，正常返回前明設 A0=0。

不同候選不可套用同一個平移量：worker 位移 168、core 與第一個 helper 位移 234，RAM service 入口則位移 76。帳本各自固定原始呼叫指令，並只記錄第二個服務的候選 first-copy entry mapping；**沒有宣稱已驗證它的完整 body、輸出、實際安裝或物理效果**。

## 接回 selector 的條件性結果

[已驗證的 check3 wrapper](v4160-b1-selector-callees-static.zh-TW.md)傳入 `(P,自身SP+8,自身SP+12)`。SP+8..10 是從 query+3 複製後的三個 bytes，其中 SP+10 先改為 `(byte&63)|64`。Worker 的第二個來源 V 是這個 scratch，不是直接拿原始 query pointer；輸出 O 是 wrapper 的 SP+12..14。

- allocator 返回 null：worker=19，wrapper 非零返回，上層 selector 跳過候選，不做最後三個 bytes 比較。
- 配置非零、匹配的 core 外層與所有依賴正常返回／保存 frame：core=0，worker 最終回傳保存的零，wrapper 才請求最後 comparator。
- wrapper 的最後正規化只有 comparator **完整返回 1** 才得到零；不能因 core=0 就推出資料有效或比較成功。

即使內層服務回傳錯誤 scalar，core 外層也會在正常路徑返回零；worker 接著仍嘗試輸出 copy 與 release。這個局部控制流證據無法替代 provider 的輸出、完成、ownership、no-retention 或完整指標保存期合約。

下一步仍需展開 `63eda / 63fc4`、`200022be / 2000230a`，追查動態 context pointer writers 與實際 provider 綁定。這份結果不是硬體功能、演算法輸出或可用韌體的實測重現。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_worker_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_worker_static.py
```

檢查拒絕 182 個逐指令 mutations 與 4 個 typed-load mutations；驗證長度 0..256 的 32,896 組倒序來源／目的 index、實際 0／3／16-byte 不可變 CFG 路徑、48-byte 及 caller frame interval，並重播確定性 JSON。這些是 host scalar／interval 證書與語法路徑，沒有在寄存器或記憶體模型中執行 worker／reverse／core。
