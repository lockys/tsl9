# v4.1.60：request 清理鏈、callback34／36 與 registrar 尾跳

本階段延續 [RF task／callback17 消費證據](v4160-b1-callback-consume-static.zh-TW.md)，展開 request 八次已完成退出後的尾跳、RF task event8 的共同 helper，以及 request 中兩處 reset wrapper。只核對原始位元組、完整 operands、不可變 CFG 路徑與 host scalar 算術；沒有執行或模擬目標 ISA、服務、RAM、timer、heap 或硬體。

[驗證程式](check_v4160_b1_request_leaves_static.py)與 [JSON ledger](v4160-b1-request-leaves-static.json)保存逐指令、分支、call、store、frame 與跨函式串接證據。

| 完整新增函式 | V131 候選範圍 | V140 候選範圍 | 每份 bytes／指令 |
|---|---|---|---|
| inner cleanup | `[0x656c6,0x6575a)` | `[0x657b0,0x65844)` | 148／50 |
| outer cleanup | `[0x6575a,0x657d8)` | `[0x65844,0x658c2)` | 126／46 |
| reset wrapper | `[0x6440a,0x64422)` | `[0x644f4,0x6450c)` | 24／9 |

合計 **596 bytes、210 條指令**。所有位元組均須存在於原始 sparse HEX 並與候選 carrier 相符，不補零掩蓋缺口。另重用完整 reset 共 260 bytes、registrar 共 44 bytes、APP status 共 76 bytes；不重算這些既有範圍，也不提高既有 C 重建覆蓋率。

## inner cleanup 的順序

令 V131 `C=0x20003560`、`S=0x20003514`、`F=C-32`；V140 對應地址加 80。inner 使用 16-byte frame，保存 RA／S0／S1，完整 CFG 為 DAG，只有普通 RET。

1. 讀取 `0x4002420c` 的 word 保存到 S1，向同地址寫零，再保留原始 `FENCE.I`。
2. 捕獲 fresh `C+4` word，**先清 `C+14` byte**，再檢查該捕獲值；非零才請求 RAM service `0x20000110(captured pointer)`。
3. 略過 release 或其正常返回後，先讀 fresh `S+9`，再無條件清 `C+4` word。此清零不取決於服務 scalar reply；亦不證明釋放成功、沒有其他引用或沒有重入更新被覆寫。
4. 若先前讀取的 `S+9` 非零，且獨立 fresh `S+8==8`，清 `S+9`。之後第一個 fresh `S+7==6`，或另一個 fresh `S+7==7` 時，再讀第三個 fresh `S+7` 寫至 `S+8`，並設 `S+9=1`。第三個值沒有被比對，不能宣稱寫入值必為 6 或 7。前面的 latch clear 亦可能被後面的設 1 覆寫。
5. 無條件呼叫完整 reset `0x63e58/0x63f42`。返回後讀 fresh `C+16` task ID，清 byte `0x20002efc/0x20002f4c`，再請求 stop `(fresh task,16)`，目標 `0x439a8/0x43a34`。
6. 將保存的原始 control word 寫回 `0x4002420c`，強制 A0=0，恢復 frame 後返回。

此函式共有八個非 frame stores：包含 control 先清／後回寫、`C+14`、`C+4`、條件性的三個 latch stores 與全域 flag 清零。control 回寫只證明寫入來源；沒有證明周邊硬體恢復。stop 的請求與其回覆不構成事件取消、timer 釋放或排程完成的確認。

## outer cleanup 的 callback 與後續清零

outer 保存 RA／S0／S1／S2 到 16-byte frame，先呼叫 inner。正常返回後依序：

- fresh `C+15` byte 寫至 `F+1`；fresh `C+20` word 寫至 `F+8`。
- 請求 stop `(fresh C+16,8)`，再以**另一個 fresh task ID** 請求 stop `(fresh C+16,4)`；不依 scalar reply 分支。
- 第一個 fresh `C+12` bit1 若設，從 fresh `F+16` word 讀 callback 並呼叫 **`(34,0,0)`**。若未設，才重新讀 `C+12`；這次 bit2 若設，呼叫 **`(36,0,0)`**，否則不呼叫。第二個 code 是十進位 36。每條本機正常路徑最多一次 callback，指標沒有 null guard。
- callback 正常返回後，或沒有 callback 時，清 `C+12` byte。恢復自身保存的 S registers／RA／SP，再以 `(A0=0,A1=2)` 無新 link 尾跳 registrar `0x43b28/0x43bb4`。

因此 callback 可以在 `C+12` 被這個 epilogue 清除之前觀察或改寫它；不能把清零視為與 callback 原子執行，也不能假設 callback 返回後其他全域值仍相同。outer 自身只有三個非 frame stores；不把被呼叫函式的 writes 算成這三個 stores 的完整副作用。

## 尾跳實際清除哪個槽位

重用完整 22-byte registrar 證據：以**完整 unsigned 入口 A1** 比對上限 4。A1<=4 時向 `table+4*A1` 寫入入口 A0，否則直接 RET。V131 table=`0x200031c8`，V140 table=`0x20003218`。

outer 的固定 `(0,2)` 因此清除 word **`0x200031d0/0x20003220`**；這不是清 `F+16` callback word。registrar 不寫 A0，故在一般保存／返回條件成立時，outer 的最終 scalar 為 0。A2 未被 epilogue 重設，不推定 tail 的其他參數或副作用。

## APP `0x174ee` 如何消費 34／36

若實際 callback 綁定仍為前階段的 APP `0x174ee`，兩個 tuple 的 A2 都是零，但這兩條路徑**不解參考 A2，也不尾跳 retry**：

| callback code | APP 內部 `(code-17)&255` | 本機出口 |
|---|---|---|
| 34 | 17 | A0=17，普通 RET |
| 36 | 19 | A0=19，普通 RET |

回傳 A0=17 並不是重新以 status17 進入 callback；兩者不可混淆。outer 會忽略這個 scalar，繼續清 flags 與 registrar 尾跳。此結果是原始 APP 分支與 host scalar 證據，沒有實際呼叫 callback。

## reset wrapper 與驗證界線

wrapper 僅保存 RA 到 16-byte frame，直接清 `C+14`，呼叫 reset `0x63e58/0x63f42`；沒有新設定 A0／A1／A2。正常返回後忽略 reply，強制 A0=0、恢復 RA／SP 並 RET。它沒有直接寫入 `C+12`，也不等於已確認硬體 reset。

驗證拒絕 **210 個逐指令 mutation、12 個 typed-load mutation**；包含完整函式 identity、QingKe 指令標記、每個本機 call／tail／store 與 CFG 邊的路徑證據。host scalar 檢查涵蓋 65,536 對獨立 flags snapshots（callback34／36／無 callback 的分區為 32,768／16,384／16,384）、65,536 對 state snapshots（511 對進入後續 latch 路徑）、256 個獨立第三次讀取值，以及 APP code／registrar 地址算術。一般與 `-O` 模式精確重放同一 JSON。

所有組合仍要求候選 ISA／mapping 與實際 provider／callback 綁定、有效 code／frame／global／object extent、callee 對 S／SP／RA／保存 frame 的遵守，且沒有破壞性 alias、wrap、IRQ／DMA 或重入。各次 fresh reads 的相等性需要獨立證據。私有 release 的實際 provider、物件完整保存期、timer 交付／取消、硬體效果及其他 writers 仍未證明。接下來剩餘 request callees 為 `0x64794/0x6487e`、`0x63c54/0x63d3e` 與 RAM service `0x200026ba/0x20002706`。

```powershell
python analysis/check_v4160_b1_request_leaves_static.py
python -O analysis/check_v4160_b1_request_leaves_static.py
```
