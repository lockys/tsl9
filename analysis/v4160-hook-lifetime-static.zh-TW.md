# v4.1.60：候選 hook 登錄、fresh flag 與清除條件

承接 [context callback 與 frame+0 來源](v4160-context-callback-frame-static.zh-TW.md)，本輪完整驗證兩份 resident **候選**中的 hook setter 與 gateway service。兩份候選的對應邏輯相同，但資料 slot 與 bytes 不同；不據此認定實際 installed provider。

結論是：setter 先存 raw pointer，非零時再寫 flag=1；service 先讀 pointer 並條件呼叫，返回後才重新讀 flag，讀到零才清除 slot。因此保留的是「當下 slot 不被這個本體清除」的條件，不能推出原 pointer、payload 或物件仍然有效。

分析只解碼原 bytes、比對 operands／CFG 與做主機端地址及分支判定算術；沒有執行或模擬目標 ISA、RAM、stack、callback、CSR、ECALL、MMIO 或裝置。既有 C 重建 bytes 未增加。

## 完整本體與映射

| 候選 | FLASH setter，end-exclusive | FLASH consumer，end-exclusive | hook slot | flag |
|---|---|---|---|---|
| V1.31 | `0x409fa..0x40a10` | `0x40a10..0x40a40` | `0x20002ef8` | `0x20002efc` |
| V1.40 | `0x40a3a..0x40a50` | `0x40a50..0x40a80` | `0x20002f48` | `0x20002f4c` |

兩份 setter 都映射至 RAM `0x2000078a..0x200007a0`，各 22 bytes／7 指令；consumer 都映射至 `0x200007a0..0x200007d0`，各 48 bytes／17 指令。合計新增驗證 140 bytes／48 指令。FLASH 與 RAM 座標的完整 operands、branch targets 均核對，沒有把兩種 PC 座標混用。

first-copy 映射分別為 `0x402b0 → 0x20000040`、`0x402f0 → 0x20000040`，end-exclusive 分別 `0x20002e74`、`0x20002ec0`；四個本體全部落在相應覆蓋範圍。先前未證明 full boot 與 second-copy 缺口的限制仍保留。資料 slot／flag 位於 first-copy code 以外，初始化 zero request 包含它們，不代表已觀察到當前為零。

| 候選／本體 | SHA-256 |
|---|---|
| V1.31 setter | `8b678d65194a574a288a1421f81f05d8b6fc16daea6420cc9fcda5d8252d0e56` |
| V1.31 consumer | `dc3baa9f4ffbd828b39dcc0e89440074819a0fc8c13af4167e0fbc5f2748f1f7` |
| V1.40 setter | `f728ba41f5362d652b9663813fc00a39b14b6ecbb3c4fa5341653c3358565334` |
| V1.40 consumer | `1153522c8e921059766a62d59640fb216ffb05bfff0c0c751b38648a7eb4b591` |

APP 仍是 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。檢查器遞迴重驗先前 APP／候選／SDK／sparse 來源合約，並在本輪 ledger 保留來源身分。

## setter：零 pointer 不會清 flag

相對 setter entry 的完整指令序列為：

```text
+00 LUI A5,0x20003000
+04 SW A0,slot_delta(A5)
+08 BEQZ A0,+20
+10 LUI A5,0x20003000
+14 LI A4,1
+16 SB A4,flag_delta(A5)
+20 RET
```

V1.31 的 `slot_delta=-264`、`flag_delta=-260`；V1.40 為 `-184`、`-180`。沒有 call、自己的 stack allocation 或 pointer 有效性檢查。

- raw A0 為零：將 slot 寫零，直接返回；flag 保留先前內容。
- raw A0 非零：先將完整 raw A0 寫入 slot，再把 flag byte 寫 1。這個先後順序不能當作跨 IRQ 的原子發布。

原 pointer 的 bit0 也被存下。是否具備有效程式碼、合理對齊、正確 ABI 與足夠保存期，都沒有由這個 setter 建立。

## consumer：呼叫前的 pointer，呼叫後的 fresh flag

相對 `0x200007a0` 的完整序列為：

```text
+00 LUI A5,0x20003000
+04 LW A4,slot_delta(A5)
+08 SP-=16
+10 SW S0,8(SP)
+12 SW RA,12(SP)
+14 S0=A5+slot_delta
+18 BEQZ A4,+22
+20 JALR A4
+22 LUI A5,0x20003000
+26 LBU A5,flag_delta(A5)
+30 ANDI A5,A5,255
+34 BNEZ A5,+40
+36 SW ZERO,0(S0)
+40 LW RA,12(SP)
+42 LW S0,8(SP)
+44 SP+=16
+46 RET
```

條件呼叫使用最初 fresh LW 的 A4，effective target 為 raw pointer `& ~1`，link=`0x200007b6`。呼叫前沒有本機 A0..A3 定義；不能憑服務名稱推定 hook 的完整參數合約。

跳過呼叫或 hook 普通返回後，consumer 才做 fresh LBU。若 hook 不返回，後段是否執行沒有保證；返回後也需要 SP、S0 與保存 RA／S0 的 stack words 仍符合本體假設。

| 呼叫後 fresh flag | 本機 slot 動作 | 不能推出的事情 |
|---|---|---|
| 零 | 經 then-live S0 將 slot 寫零 | 清除前 slot 仍等於先前 A4 |
| 非零 | 不做本機 slot store | slot 仍是原 pointer，或所指物件仍有效 |

consumer 在清除前沒有重讀 pointer 或比較其身分。因此，即使 hook 替換了 slot，只要後續 fresh flag 為零、S0／存取條件成立，本機 store 仍會清除替換後的值。反過來，非零 flag 也只抑制這次本機清除。consumer 自身完全不寫 flag，亦未建立固定 scalar return 值。

## 與先前 callback／gateway 的條件性串接

先前候選 JT2 callback 的 signed LB 與本輪 LBU 使用**相同 flag 地址**。callback 先讀 flag，緊接著 SB0，再依讀到的舊值分支。非零分支的 direct callee、MRET 與 gateway 到達條件仍未解除。

gateway 的 direct call target 已與本輪 consumer entry 精確相接。若這條路徑實際到達、consumer／hook 普通返回且 RA／SP 等保存條件成立，下一條是原 gateway 的 ECALL；本輪沒有建立 ECALL 到 `0x8448` 的實際 trap 路由。

在同一候選映射、存取有效且沒有其他寫入的條件下：

- callback 的 SB0 若一直保留到 consumer 的 fresh read，會選清 slot 路徑。
- 若 hook 期間完成 nonzero setter，flag=1 可使 consumer 跳過本機清除；這也依賴之後沒有其他 writer 改 flag。
- 若 hook 期間完成 zero setter，它已清 slot，卻不清 flag；不能把這次登錄解讀為 flag reset。

這些是原指令條件的串接，沒有實際呼叫 callback、建立 target RAM 模型或模擬 trap。未知 hook 可以修改 slot／flag／CSR／frame、重新進入或破壞返回條件，故不能把上列串接報為實際執行軌跡。

## 重播與剩餘邊界

[檢查器](check_v4160_hook_lifetime_static.py) 與 [完整 ledger](v4160-hook-lifetime-static.json) 可重播：

```text
python analysis/check_v4160_hook_lifetime_static.py
python -O analysis/check_v4160_hook_lifetime_static.py
```

一般及 `-O` 模式均須逐 byte 重現 ledger。檢查覆蓋完整四個本體、映射、相同 flag／gateway 接點、256 個 byte 的 LB／LBU 零判定，以及 26 個指定原指令 operand mutation；mutation 必須被對應 operand 或 unsigned-byte 編碼檢查拒絕。

下一步仍需找 setter 的實際 callers 與 pointer 來源、其他 flag writers、callback 的兩個 direct callees、實際 installed provider、ECALL 路由及更廣的 frame／payload 保存期。本輪不是所有 writers 的普查，也未增加 C 重建覆蓋。
