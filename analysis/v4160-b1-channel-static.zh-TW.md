# v4.1.60：完整 channel helper 與 attempt 回覆來源

本階段展開 attempt 的最後一個本機 callee `0x63b0e/0x63bf8`，接回原本只知道「最後 helper 回覆」的返回鏈。只使用原始位元組、完整 operands、不可變 CFG 與 host scalar／區間算術；全程離線，沒有執行或模擬目標 ISA、provider、RAM、control registers 或硬體。

[驗證程式](check_v4160_b1_channel_static.py)及 [JSON ledger](v4160-b1-channel-static.json)保存完整證據；前置證據見 [配置 helper／attempt A1=0](v4160-b1-frequency-static.zh-TW.md)。

| 完整函式 | 原始範圍 | bytes／指令 |
|---|---|---|
| V131 resident 候選 | `[0x63b0e,0x63c54)` | 326／124 |
| V140 resident 候選 | `[0x63bf8,0x63d3e)` | 326／124 |

新增 **652 bytes、248 條指令**。每個位元組均符合原始 sparse HEX，不以補零填缺口。重用完整 attempt 共 1,004 bytes，不重算新增範圍，也不提高既有 C 重建覆蓋率。

## 完整本機範圍與 snapshots

函式沒有 frame、calls、尾跳或迴圈；CFG 為 DAG，兩個普通 RET 在 +0x78／+0xe4。共 23 個 byte／word store sites，GPR definitions 為 A0..A7、T1、T3，沒有 S／SP／RA 寫入。

令 V131 `G=0x20003000`、狀態 `S=G+1300`、R slot=`G+1288`、H slot=`G+1340`；V140 各 offset 加 80。入口 optional descriptor=`[G+1292]` 若非零，會先經 descriptor+16 的指標，將 mask descriptor+20 OR 入目標 word；再經 descriptor+0 指標，將 mask descriptor+8 OR 入另一個目標 word。只有 descriptor 本身有非零 guard，兩個內層指標沒有 guard，亦不假設兩次寫入為原子操作。

其後依序捕獲 fresh R、fresh byte **s=S+10**、fresh H0。R／H0 沒有本機 null guards。entry A2 在使用前被覆寫，實際 mode 使用完整 A0，數值參數 a 使用完整入口 A1。

## 四類 mode 的 R+0 更新

| 完整入口 mode | R+0 的本機寫入 |
|---|---|
| mode==1 | fresh word AND `0xffffcfff`，清 bits12／13 |
| mode!=1 且 bit1=0 | fresh word AND `0xffffcfff` OR `0x1000` |
| bit1=1 且 mode!=3 | 先清 bits12／13 並設 bit13；再以另一個 fresh word AND `0xffff3fff`，清 bits14／15 |
| mode==3 | 先清 bits12／13 並設 bit13；再以另一個 fresh word AND `0xffff3fff` OR `0x4000` |

bit1 路徑有兩次獨立 R+0 observations，不能合併成單一 RMW 或假設第二次保留第一次所設的位元。完整 mode=5 屬於第二列，mode=7 屬於第三列，沒有先縮成 low byte 或只接受 0..3。

## 所有 mode 共通的 H0／H1 路徑

每一條 mode 路徑都依下列順序：

1. 在完成該路徑的 R+0 寫入**之後**，從先前捕獲的 H0+12 讀取完整 word B 到 A0。B 不是入口時就取好的 snapshot。
2. 將 `B & 0xffffdfff` 寫至 H0+12，清 bit13。
3. 保留兩個原始 `0x0100` NOP／hint bytes；未推定硬體等待或同步語義。
4. 重新讀 H slot，取得 fresh H1。依序寫入 H1+8=8192、S+4 byte=128、H1+100=duration，最後 **H1+12=B**。
5. 普通 RET；A0 沒有再被覆寫，回傳完整 B。

因此 H0 與 H1 不必相同。「把原值寫回」的來源是 H0，而目的地可以是不同的 H1。它不證明相同硬體物件已恢復，也不證明沒有其他保存指標或副作用。A0 返回值不是 duration、零或既定 success status。

## duration 的指令算術

所有計算取 low32，s 是前面捕獲的 unsigned byte，a 是完整入口 A1。

| mode 類別 | 原路徑算術 | 等價 scalar |
|---|---|---|
| bit1=0、非1 | `2*(s+158+8*(a+10))` | `16*a+2*s+476` |
| 完整1 | `2*(s+158+4*(a+11))` | `8*a+2*s+404` |
| bit1=1、非3 | `2*(s+190+8*(8*(a+2)+74))` | `128*a+2*s+1820` |
| 完整3 | `2*(s+190+2*(8*(a+2)+215))` | `32*a+2*s+1304` |

第一列的淨 a 係數是 **16**：先 shift3，再於共同尾段 shift1。這些只證明 word+100 的寫入來源，不推定時間單位、硬體 channel 意義或飽和處理。

## 接回 attempt128 的實際參數與回覆

完整 attempt128 路徑將保存的 A1 設為 2，在 clock 間接呼叫前 spill 至 SP+12，返回後 reload，至 +0x152 呼叫 channel helper 前沒有再改 A1。A0 則使用另一個 fresh config byte 的 bits4..5，故這個 caller 的 mode 範圍為 0..3。

| caller mode | a=2 的 H1+100 寫入 | s=0..255 時的範圍 |
|---|---|---|
| 0 | `2*s+508` | 508..1018 |
| 1 | `2*s+420` | 420..930 |
| 2 | `2*s+2076` | 2076..2586 |
| 3 | `2*s+1368` | 1368..1878 |

channel 返回後，attempt 仍執行自己的 control／status writes，然後恢復 frame，但沒有再寫 A0。在正常存取、code／frame 保存等條件下，這條 attempt 路徑的最終完整 scalar 因而可具體定位為上述 **mode-specific H0+12 捕獲值 B**。這比「最後 callee 的未知回覆」更精確，但仍不是物理完成或成功的確認。

## 驗證與尚未閉合事項

驗證涵蓋完整 operands／typed loads、QingKe byte accesses、八個原始 hints、23 個 stores、GPR clobber envelope、全部 CFG 邊、四類 mode／optional descriptor witnesses，以及 H0 capture 到 H1 restore 的順序。拒絕 **248 個逐指令 mutation、16 個 typed-load mutation**。

host scalar 檢查涵蓋 65,536 個 mode 低16位值、1,048,576 組 duration identity 案例、四個 a=2 模式下的全部 s bytes，並核對完整 word 的 wrap 邊界。mode／a 的低16位是測試域，完整分支與 low32 代數合約以原指令為準。一般與 `-O` 模式精確重放同一 JSON，沒有可變目標狀態模型。

實際 matching provider、有效 descriptor／R／H／global extent、一般記憶體完成、無破壞性 alias、IRQ／DMA／重入／外部 writers 等仍是前提；各次 fresh reads 的相等性須另證。動態 writes 若碰到 code 或 caller frame，不能只從沒有 S／SP／RA definitions 推定整體保存。後續仍需展開 callback `0x65de6/0x65ed0`、C+12 completion writers、設定／mask／divisor／K 的來源約束，並確認實際綁定、所有 polling 進展與完整指標保存期。

```powershell
python analysis/check_v4160_b1_channel_static.py
python -O analysis/check_v4160_b1_channel_static.py
```
