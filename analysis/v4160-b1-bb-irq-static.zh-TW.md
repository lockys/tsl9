# APP BB 中斷至 RAM JT1：完整 handler 與 clock 來源

接續 [JT120 名義介面與來源驗證](v4160-b1-dispatch-sources-static.zh-TW.md)，本輪沿 APP 的實際向量及 RAM 指標讀取位置，完整核對另一條 **BB 中斷入口**。它使用 RAM JT1，不是 FLASH JT120；兩者不能因都與計時／中斷相關而合併。

新增核對兩版候選各 **244 bytes／91 條指令**的完整正常入口本體，合計 **488 bytes／182 條指令**，另核對 APP 12-byte／4-instruction shim。[Python checker](check_v4160_b1_bb_irq_static.py) 與 [固定 JSON ledger](v4160-b1-bb-irq-static.json) 保存原始指令、operands、hashes、完整本機 CFG、frame／A0 def-use 及來源連接。

全程只讀原始 bytes 與 strict sparse HEX，使用不可變 CFG、暫存器定義與封閉整數關係；沒有執行／模擬目標、中斷、clock、MMIO 或可變 provider 狀態。

## 向量、指標發布與 first-copy

APP 向量 word `0x8134` 為 `0x1873e`。該入口的完整 shim 是：

```text
0x1873e  LUI A5,0x20000000
0x18742  LW A5,4(A5)
0x18744  JALR A5             # link=0x18746
0x18746  MRET
```

它讀取絕對位址 **RAM[0x20000004]**，不依賴 GP，沒有本機 null guard、frame 或 A0/A1 初始化。正常返回後直接進入 MRET，沒有讀取或還原 A0。這只說明編碼的控制流；硬體 interrupt ABI、shadow registers、CSR 及受中斷狀態的完整保存尚未證明。

| 候選 | RAM JT1 目標／完整本體 | FLASH 來源 | bytes／指令 |
|---|---|---|---|
| V131 | `[0x2000251c,0x20002610)` | `[0x4278c,0x42880)` | 244／91 |
| V140 | `[0x20002568,0x2000265c)` | `[0x42818,0x4290c)` | 244／91 |

重用 [原始初始化器](v4160-dispatch-origin-mask-static.zh-TW.md) 的完整 114-byte 本體，確認 `+0x1a` 將上述 entry 寫入 RAM[0x20000004]。該發布發生在第一筆 code-copy 呼叫之前；**槽位已發布不代表當時 code 已準備完成**。本輪核對完整 244-byte 來源均在 first-copy 映射與實際捕獲 HEX 範圍內，但不據此聲稱 copy 曾完成、installed code 一致，或中斷實際到達的時間。

## 本機行為：fresh 指標、軟體 flags 與唯一 clock 呼叫

令 G=`0x20003000`，各欄位分別為：

| 角色 | V131 | V140 |
|---|---|---|
| R 指標槽 | G+1288 | G+1368 |
| 軟體 context H | G+1300 | G+1380 |
| T 指標槽 | G+1340 | G+1420 |
| K 指標槽 | G+1284 | G+1364 |
| clock 指標槽 | G+480 | G+560 |

這裡 H 不等於前輪登記 context C。不同時間的 fresh pointer／word／byte 取樣均保留為獨立值，不能直接合併。

正常入口先讀 R0，配置 16-byte frame，保存 S2、S1、S0、RA。其後行為如下：

1. 初次 `U32[R0+56]` 的 bit6 為零時，跳過全部初段 H 操作，直接到 `+0x96` 的 fresh R1 階段。
2. bit6 非零時，寫 **完整 word 96** 到同一 held R0+56，並形成 H。
3. fresh H+0 byte 的 bit6 非零時，從 clock 槽讀入目標並 linked call，沒有 null guard。傳給它的是尚未由本機改寫的 **ambient A0/A1**。回覆 A0 寫入 H+28，然後重新讀 H+0，以 AND 191 清除 bit6。
4. 接著獨立檢查 fresh H+0 bit5；若設置，另一次 fresh byte AND 223 store 清 bit5，再讀 T0，寫 T0+8=32768、T0+108=`low32(U32[H+20]<<1)`。
5. fresh H+4 bit6 未設時，寫 H+5=1；另讀 T1，寫 T1+8=8192、H+4=192，以及 T1+100=fresh U32[H+16]。T0、T1 不保證相同。

上述 3–5 全都位於初次 R0 bit6 的非零分支內。clock 可改變外部狀態；其回覆、可達性與返回都不能由本機分支名稱推定。

所有路徑接著在 `+0x96` 重新讀 R1：

- fresh U32[R1+56] bit4 非零：寫完整 word 16 至 held R1+56，再寫 H+4=1。
- **再次讀取**同一 held R1+56，bit7 非零：寫完整 word 128，再寫 H+4=1。
- 另讀 K，fresh U32[K+4] bit1 設置時，先以另一筆 fresh K+4 AND -3 寫回，再重新讀 K+4，以 AND -2 寫回。

最後兩筆是分開的 fresh-read RMW，不是原子清除兩個 bit。對 R/T/K 指向範圍的 word stores，只證明原始指令的數值與位址關係；尚未證明硬體 W1C、ack、清除中斷、同步或時序效果。

## 本機 frame 與 A0 保存界線

完整 handler 的 sole RET 在 `+0xf2`。四個 word save／restore 對應為 S2@0、S1@4、S0@8、RA@12，SP 只有 `+0x08:-16` 與 `+0xf0:+16` 兩個定義。checker 核對正常路徑中的 frame 配置、還原與 S1=H 的支配關係。

handler 本身沒有 A0/A1/GP 定義。clock 未呼叫時，RET A0 仍為入口值；clock 正常返回時，RET A0 為其回覆，並已在 H+28 捕捉。APP shim 在 MRET 前不使用該 scalar。這不代表原先受中斷的 A0 已保存，也不保證未知 clock 遵守所需的 S/SP/RA 與 frame 保存條件。

全部本機分支 successor 都位於這個 244-byte 範圍，唯一外部呼叫為 `+0x3c` 的 clock。據此稱為「完整正常入口本體」，不因 RET 後還有 bytes 就推定後續不存在其他入口。此本體沒有直接讀取 JT120 表項；未知 clock 的遞迴或 transitive 行為仍未排除。

## 指標與 APP clock 的條件性來源

重用 [radio config parent](v4160-radio-config-chain-static.zh-TW.md) 的完整 118-byte 本體，確認在第一個 linked call 之前，編碼即發布：R=`0x40024100`、T=`0x40024200`、K=`0x40024300`。這是候選 producer 的本機 store 證據，尚未證明呼叫順序或這些值在中斷期間保留。

另重用 [APP clock 設定來源](v4160-service-provider-link-static.zh-TW.md) 與 [完整 config gates](v4160-config-gates-static.zh-TW.md)：APP `0x19bba` 的設定 prefix 形成 `0x191c6`，候選設定程式由 fresh copied/default D+0 發布至 G+480／560。若實際設定、copy 及 installed binding 均匹配，handler 的 clock 便可接至完整 90-byte APP reader `[0x191c6,0x19220)`。

該 reader 沒有 stores、nested calls、frame 或 S/GP/RA 定義，且先覆寫 A0 才使用它，因此不會在本機解參照、發布或保存 handler 傳入的 ambient A0。它仍有多個讀取重試迴圈；**不保證硬體讀取穩定或迴圈終止**。generic fresh clock 尚不能一律當成這個 reader。

## 驗證與後續

```powershell
python analysis/check_v4160_b1_bb_irq_static.py
python -O analysis/check_v4160_b1_bb_irq_static.py
```

每版 CFG 有 **97 條 edge、72 條 DAG 語法路徑**；每條 edge 都有入口至 sole RET 的有限見證。這些不是 target traces 或實際可行輸入。完整 body 有 20 個 stores，其中 4 個 frame stores、16 個其他 stores；五個 Xwchc byte 指令逐一固定 bytes／mnemonic，未使用 stock r2 的浮點別名解釋。

負向核對包含 **186 個逐指令變異、20 個 typed-load funct3 變異**，另有全部 256 個 flag byte 與 65536 個 low16 scalar 樣本的封閉等式核對；沒有建立 clock、硬體或 IRQ 狀態模型。原有驗證鏈、APP／SDK／候選身份、strict sparse HEX 與固定 ledger 也一併重跑。

仍需確認 RAM JT1 的實際 installed code、發布／copy／IRQ 時序、其他 H／指標槽 writers、clock 綁定與重試進展、硬體 interrupt ABI，以及 JT120 的實際 caller 和完整消費釋放保存期。本輪增加候選本體靜態合約，**APP C 重建覆蓋不變**；既有約 95.75% 快照不等於完整韌體已可用。
