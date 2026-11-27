# v4.1.60：配置 helper 與 attempt 的 A1=0 路徑

本階段展開 attempt 的直接 callee `0x6434a/0x64434`。只分析原始位元組、operands、不可變 CFG 與 host scalar 算術；全程離線，沒有執行或模擬目標 ISA、provider、RAM、除法狀態機或硬體。檔名沿用配置主題，不據此認定欄位具有實際頻率或時間單位。

[驗證程式](check_v4160_b1_frequency_static.py)及 [JSON ledger](v4160-b1-frequency-static.json)保存完整證據；前置呼叫鏈見 [sampler 內層保存驗證](v4160-b1-sampler-inner-static.zh-TW.md)。

| 完整函式 | 原始範圍 | bytes／指令 |
|---|---|---|
| V131 resident 候選 | `[0x6434a,0x6440a)` | 192／66 |
| V140 resident 候選 | `[0x64434,0x644f4)` | 192／66 |

新增 **384 bytes、132 條指令**。每個範圍都逐位元組符合原始 sparse HEX，不以補零填缺口。重用兩份完整 attempt 共 1,004 bytes，不重算新增範圍，也不提高既有 C 重建覆蓋率。

## 真正使用的入口參數與回傳值

令 `G=0x20003000`，V131 的設定 F=`G+1344`，D pointer slot=`G+1424`，R pointer slot=`G+1288`；V140 各 offset 加 80。

函式先把 A0 覆寫為 G，再建立 F 地址並覆寫 A2。因此入口 A0／A2 都不作輸入，**只有完整入口 A1** 決定分支。所有普通路徑的唯一 RET 均回傳固定 **A0=`0x20003000`**；它不是 0，也不是已證明的硬體成功確認。

本機沒有 frame、calls、尾跳或迴圈；所有 GPR definitions 僅為 A0..A7，沒有 S／SP／RA 寫入。完整 CFG 為 DAG，共七個 word store sites。

## 初始指標與 A1=0 路徑

入口分別捕獲 fresh D 與 R，沒有本機 null guards，也不在後段重新讀取 pointer slots。接著讀取 fresh byte F+1，保存其 low7。

完整 A1=0 時：

1. 讀 fresh D+44 word，清 bit1 後寫回。
2. 讀 fresh R+0 word，以先前保存的 F+1 low7 取代其低七位，其餘位保留，寫回 R+0。
3. 進入共同尾段。

這條路徑不讀 F+4，也不執行 DIVU／REMU 或兩個 D+68 writes。

原始 attempt 的 +0x62 明設 A1=0，到 +0x76 呼叫之前沒有再寫 A1。它雖然另讀 fresh F+1 到 A0，該值會被 helper 覆寫而不使用。因此上述零路徑確實對應這個 caller；不能將 nonzero 分支的除法結果套在 attempt 的這次呼叫上。後續 attempt 在 clock／channel 使用前會再覆寫 A0，不能把固定 G 當成那些服務的回覆。

## nonzero A1 的兩段算術

非零分支先捕獲 fresh word X=F+4，並向 R+0 寫入同樣的 low7 replacement。調整 X 的規則使用完整 A1：

| A1 條件 | 調整後 X |
|---|---|
| 非零且 bit0=0 | 原始 X |
| bit0=1 且 `(A1 & 0x30)==0x10` | `low32(X-2000)` |
| 其他 bit0=1 | `low32(X-1000)` |

這是 unsigned wrap，不是飽和或負值 clamp。例如完整 A1=0x100 的低 byte 雖為零，仍屬於非零 even 分支。

之後先把 fresh D+44 的 bit1 設為 1，再以固定正除數計算：

```text
q = unsigned X / 64000
r = unsigned X % 64000
第一個 D+68 write = (fresh word & 0xfe0fffff) | ((q & 31) << 20)
第二個 D+68 write = (另一個 fresh word & 0xfffc0000)
                   | (((r << 10) / 250) & 0x3ffff)
```

第一個 RMW 更新 bits20..24；第二個更新 bits0..17。兩次 D+68 observations 獨立，不能宣稱第二次必定保留第一次寫入的 quotient bits，也不是一筆原子更新。

由 r<64000 可得 `r<<10` 不會 overflow U32，fraction 最大為 262139，確實容於 18 bits。完整 quotient 最大為 67108，但程式只取其 low5，沒有飽和或超界拒絕。

## 共用尾段的兩次 R+0 observations

所有分支最後都重新讀取 fresh byte F+0。若 bit1 清除便 RET；若設位則：

- 從第一個 fresh R+0 擷取 low7 並 OR 0x40。
- 重新讀另一個 fresh R+0，保留其 upper25 bits。
- 將這兩個不同來源合併後寫回 R+0。

這裡沒有再使用最初保存的 F+1 low7，亦不假設兩次 R+0 相同。若有外部改寫，最終低位與高位可以來自不同狀態；原指令只證明來源、順序與寫入形狀。

## 驗證與保存界線

驗證固定所有 operands、typed loads、QingKe byte load、unsigned DIVU／REMU modes、七個 store sites、唯一 RET、GPR clobber envelope、完整 CFG 與八條選定分支 witness。拒絕 **132 個逐指令 mutation、6 個 typed-load mutation、6 個 arithmetic-mode mutation**。

host scalar 檢查涵蓋 65,536 個 A1 低16位案例（zero／nonzero even／odd-1000／odd-2000 分區為 1／32767／24576／8192）、全部 64,000 個 remainder、67,109 個 quotient，以及 32,768 組獨立 low7／high-byte 合併。低16位是驗證域，完整入口 A1 合約仍以原指令為準。一般與 `-O` 模式精確重放相同 JSON。

函式不直接保存入口指標，且沒有 nested call；但對動態 D／R 的寫入仍依賴有效 extent（至少 D 72 bytes、R 4 bytes）、普通記憶體完成與無破壞性 alias。若 D／R alias code、caller frame、設定來源或硬體映射，不能從 GPR 保存合約推成物件／frame 完整保存。

實際 installed provider、欄位硬體意義、fresh observations 的相等性、atomicity、IRQ／DMA／重入與完整指標保存期仍未證明。下一個主要 callee 是 `0x63b0e/0x63bf8`，另需追查 callback 本體及設定／mask／divisor／K 的 writers 與可達約束。

```powershell
python analysis/check_v4160_b1_frequency_static.py
python -O analysis/check_v4160_b1_frequency_static.py
```
