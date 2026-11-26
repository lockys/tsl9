# v4.1.60：40058 timer 候選、small split 與第二次 task 登記

接續 [registration 返回鏈](v4160-registration-return-chain-static.zh-TW.md)，本輪展開 fresh `40058` 的完整候選服務及 RAM lookup，並串接返回 setup 後的 `907a`。在明示的額外 fresh 狀態與保存條件下，可封閉「threshold 拒絕回 0」或「建立新 node 回 1」兩類路徑；setup 沒有檢查這個回覆，接著都可進行第二次 task 登記。

若後續 matching fill／registration 與 table 保存條件成立，第二次登記返回 `4`、count 改為 `5`，並在 `20004804` 寫 callback address `901a`。證據止於 setup `8eb6` 的下一次間接呼叫之前，未執行 `401a0` 或任何候選服務。

程式：[check_v4160_timer_start_setup_static.py](check_v4160_timer_start_setup_static.py)。證據：[v4160-timer-start-setup-static.json](v4160-timer-start-setup-static.json)。只有原 bytes／operands／CFG 與封閉整數、區間等式；沒有 target ISA、timer／heap／RAM 狀態模型、callback、MMIO 或裝置執行／模擬。C 重建覆蓋率不變。

## 完整原本體

| 候選 | 40058 服務（右端不含） | RAM lookup 來源 |
|---|---|---|
| V131 | `43728..43874` | `40584..405a2` |
| V140 | `437b4..43900` | `405c4..405e2` |

服務每版 332 bytes／113 指令；lookup 每版 30 bytes／11 指令，候選 copy mapping 對應 runtime `20000314`。各本體完整 hash、指令與 CFG 均記於 JSON。服務唯一 local SCC 是三節點 append traversal；lookup 也有搜尋 SCC，不能假設任意 list 會終止。

服務進入時建立 48-byte frame，保存 RA／S0..S7 共九個 word。先讀 `4002420c` snapshot、寫零並遇到 FENCE.I；本輪僅辨識原指令，沒有執行。必要的正常完成、saved words 完整與無不利硬體副作用仍是前提。

## 實參與 threshold

前輪 wrapper 尾跳提供 `(task,event,delay)=(3,8192,192000)`。原 count=4 時通過 task-index gate；fresh service word 必須保持 `191c6` 才能接到已驗證 APP reader。這是 `200031e0／20003230`，並非上一輪保存 resident clock callback 的 `20003230／20003280`；不同候選的相同數字也不能混成同一版狀態。

服務以 copied config 的 fresh halfword h 形成精確 unsigned 64-bit `h*192000+800`，A1:A0 為 high:low，A2=1600、A3=0，呼叫完整的一般算術 helper。前輪只封閉該 helper 的控制流與保存，故本輪仍把 A0 回覆記為 opaque D0，沒有宣稱 quotient 數值。

threshold 是 `(fresh U32[copied+4]−30000000) mod 2^32`；保持前輪 word4=`ffffffff` 時為 `fe363c7f`。若 unsigned D0 大於 threshold，恢復 control snapshot、frame 後返回 0；否則繼續讀取 reader。返回 0 不代表發生例外，也不證明已有 timer。

reader 回覆記為 R；第二次使用 fresh h 與原 delay 形成同樣形式的 helper 請求，A0 回覆記為 D1。deadline 只依原指令定義：

```text
sum = (R+D1) mod 2^32
若 sum<D1（carry）或 sum>=fresh word4：
    deadline = (sum−word4) mod 2^32
否則：
    deadline = sum
```

這是最多一次 subtraction，不能概括成一般 modulo，也未指定時間單位、硬體進度或實際送達。

## 新 node 路徑的額外 fresh 前提

除了前輪所有 matching code／slots、有效存取、frame／heap／global 非別名與無外部干擾等條件，本輪新 node 路徑**額外要求**在服務入口及所需讀取時：

- list head 為零，並保存到 lookup 與 append 判斷時。
- allocator small head=`A=200043ac`；A 的 next=`B=200045ac`、size=504、tag=0；sentinel=`E=2000b184`，相關 global／headers 有效且保持。

post-config 的最初 head clear 與 [heap／首次配置證據](v4160-initial-table-extent-static.zh-TW.md) 提供來源見證，**沒有把它們當成所有中間 writers 都保存這些 fresh 值的證明**。因此這是條件式路徑，而非實機首次排程觀測。

空 head 使完整 lookup 直接回 0。服務隨後以 size=16、tag=`(3 OR −256)&ffff=ff03` 呼叫 matching runtime `20000040`。重驗 [完整 allocation core](v4160-allocation-core-static.zh-TW.md) 的 small-fit 分支可得：

| 項目 | 條件式結果 |
|---|---|
| 配置 header | `200043ac` |
| 16-byte payload／timer node | `200043b4` |
| 新 free header | `200043c4` |
| 新 free size | 480 |
| account halfword | 原值減 24，依 U16 store 語意 |

本分支不進 allocator search／fallback。node 與 head stores 為：byte0=3、byte1=1、halfword+2=8192、word+4=0、word+8=deadline、word+12=0，head 指向新 node。六個欄位均落在 owned 16-byte payload 內；head=0 使 append cycle 不可達。恢復 control snapshot 與 frame 後返回 1，**不代表 callback 已執行或 event 已送達**。

其他 existing-node、allocation-failure／fallback 與一般 append 路徑已完整解碼，但未在本輪封閉其所有 transitive effects 或 traversal 進度。

## 返回 setup 與第二次登記

若前輪 setup／wrapper 的 RA 與 frames 保存，`19b54` 尾跳保留的 RA 是 `8eb0`。服務普通 RET 可回到該處，並還原其 RA／S0..S7／SP。setup 直接 JAL `907a`，沒有檢查 timer 的 0／1 回覆。

完整 `907a..90b0` 為 54 bytes／19 指令，另重驗 `8eb0..8eb8` 的 8-byte／3 指令 bounded window：

1. matching `40048=2000039c` fill，以 `(2000be08,0,180)` 清除 `[2000be08,2000bebc)`。
2. fresh `40080` 接到完整 registration leaf，以 A0=`901a` 登記。
3. 若 n=4、capacity≥14、T=`200047f4` 與 allocation ownership 保持，返回舊 n=4，count 寫5，於 `T+16=20004804` 寫 `901a`。
4. APP 將回覆低 byte 寫至名義 `GP+166=200040a6`，還原 frame 後 RET 至 `8eb2`。

fill、small allocation、node 與第二次 table writes 的範圍均交叉檢查：不碰第一筆 APP callback entry3、task byte `20004184`、count／capacity／table pointer、copied config、service word 等所需 live ranges。stack 與實體 alias、MMIO／FENCE.I／IRQ／DMA／重入／外部 writers 的條件仍不能單憑數值地址分離排除。

`8eb2` 從 `[S0+416]` fresh 載入 callee，若 S0=40000 保持，來源才是 `401a0`；`8eb6` 尚未被接通或執行。此處沒有新的參數設定，但 matching fill 不改 A1，registration 不改 A1 且唯一 A2 定義是 admitted n+1，因此可將當下實參進一步收斂為 **`(A0,A1,A2)=(4,0,5)`**。這些條件式暫存器值不等於下一服務的已知 ABI。

## 驗證與後續

一般與 Python `-O` 均要求 ledger 逐 bytes 一致。檢查包含原檔身分、完整服務／lookup／APP operands 與 CFG、每版四條選定 timer 路徑（共八條）及 small-core 分支、small split／欄位界線、298 個 operand mutations、兩個非 canonical FENCE.I 編碼的 decoder 拒絕、65,536 個 wide-product／carry 等式及全部 256 種 table layout。

下一步是 fresh `401a0` 與 setup 後續，以及 head／small header 的實際保存來源。實際 provider 綁定、一般算術數值結果、其他 list 路徑、硬體進度與物件保存期仍待釐清。
