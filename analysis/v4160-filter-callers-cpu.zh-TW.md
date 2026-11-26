# v4.1.60：18BA2 的其他 caller 與保存 selector 分流

2026-11-26。接續 [18BA2 靜態合約](v4160-18ba2-static.zh-TW.md)，本批補 `129C4` 的 14 筆全零資料迴圈、`12A6E` 的單筆記錄，以及 `12AA0` 尾跳前的 selector 重讀。

原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。只在有限 CPU 與合成記憶體執行 caller 原指令；`1070A`、`16C72`、`16DAC` 及 `18BA2` 均在入口停止，沒有執行 MMIO、provider、設備或實際傳輸。

既有 `src/native/receive/callback_flow.c`、`src/native/runtime/safe_gap_functions.c` 與 [selector 靜態說明](v4160-selector-reload-branches.zh-TW.md) 已保存這些流程。本批補可重跑的原指令驗證，不改 C、共享 CPU、原 BIN 或 seal，不增加 C 覆蓋率。

## 原 APP 的三個 raw 直接轉移候選

對所有 halfword-aligned 位置掃描 JAL、RV32 C.JAL 與 C.J 的原始 encoding，目標為 18BA2，得到：

| 呼叫點 | 已核對的局部來源 |
|---|---|
| 12986，JAL RA | 已驗證的 128FE：112-byte 工作區轉成 14 筆記錄。 |
| 129F2，JAL RA | 129C4：14 筆全零資料記錄，index=0..13。 |
| 12A90，JAL RA | 12A6E 零 selector 分支：單筆 index=0、scale=1 的記錄。 |

這是 raw encoding 候選清單，加上已定位的局部指令／caller 驗證；不是完整 CFG caller census，不排除間接轉移、計算入口、不同指令邊界或其他未分析來源。

scanner 另以四種零位移 JAL／C.JAL／C.J／no-link 形式，以及原 APP 的四個已知負位移 encoding 作控制，包含最後 2-byte 邊界。沒有因為全檔掃描只有三個匹配，就宣稱整個 APP 只有三種可達 caller。

## 129C4：完整重建 14 筆零資料記錄

令入口 SP=P，64-byte frame F=P−64，R=F+12=P−52。原碼保存 S0、S1、S2、S3、RA，使用 index 0..13。每輪都完整重建 20-byte 記錄：

```text
R+0..9  = 0
R+10    = index
R+11    = 1
R+12..15 = word 0
R+16..19 = word 1
```

store 順序為 R+8 的 zero-word、R+10 的 index byte、R+12 的 zero-word、R+11 的 byte 1、R+0 與 R+4 的 zero-word，最後 R+16 的 word 1。

在 `129F2` 呼叫入口，A0=R、RA=129F6、SP=F；live S0=index+1、S1=14、S2=S3=1。本批在每次入口後明示正常返回，依完整靜態 body 的 GPR 集合保存 A0 及 S/RA/SP/GP；A1..A6 只提供未知合成值，不建立 MMIO 模型。

1,024 組單獨迴圈為 256 種非零辨識樣式 × 四個 SP mod 4。每輪前 13 次呼叫後另把 R 全部改成 A5，確認下一輪會重建完整 20 bytes。精確比對全部資料存取與映射記憶體寫入範圍，frame 洞位保持原值。四種 residue 只代表 byte-array 模型中的存取，不能推定真機接受未對齊 stack。

依既有靜態合約，這些記錄提出 scale bit clear、mode bit set、FIFO bit clear、晚段 enable bit set，兩個資料 word 為零；數值資料位址範圍仍是 `[40006640,400066B0)`。這不是觀測到的設備狀態。

在正常完成的前提下，原 epilogue 恢復 RA、SP、S0..S3，A0 保留 R=P−52，並非成功碼；該值指向已恢復 frame 的舊記錄位置。

## 12A6E：先保存 selector，零值才建單筆 scale=1 記錄

此入口配置 64-byte frame F，先將完整 A0 存到 F+12、保存 RA 於 F+60，再呼叫 `1070A`，RA=12A78。

本批不執行 `1070A`；測試明示其正常返回並保存 S/GP/SP 與原 frame，破壞 A/T，提供不同 A0 reply。原 caller 從 **F+12 重新讀完整 word** 後分流：

| 讀回 word | 原 caller 行為 |
|---|---|
| 0 | 建立 R=F+28=P−36 的 20-byte 記錄，呼叫 18BA2 一次，RA=12A94。 |
| 任意非零 | 把該完整 word 留在 A0，呼叫 16C72，RA=12A9E；不建立記錄。 |

零值記錄由三個 zero-word、R+12 的 zero-word 後寫 byte 1、R+16 的 word 1 組成；最終為前 12 bytes 全零、word[R+12]=1、word[R+16]=1。

因此 index=0、mode=0、scale=1、FIFO=0、enable word=1。相對 129C4 的記錄，這條路徑選擇另一個 scale 分支與 mode clear 分支；資料 halfwords 皆零，兩個資料 word 仍為零。

靜態消費合約只在 host 端做欄位／位址代數核對，沒有執行 18BA2。其正常返回前提給出 A0=R，原 caller 再恢復 RA/SP，故最後為 P−36。非零分支則只在 16C72 入口核對參數；要驗證 caller epilogue 時，另明示該 callee 保存 frame／S 並返回合成 reply，A0 reply 原樣流出。

## 12AA0：尾跳前已恢復 frame

此 wrapper 配置 32-byte frame F=P−32，把 A0 存在 F+12、RA 存在 F+28，呼叫 1070A 後，同樣從 F+12 重讀完整 selector：

- 零值：恢復 RA、SP 後尾跳 129C4，入口 SP 已回到 P。
- 非零：恢復 RA、SP 後尾跳 16DAC，A0 為讀回的完整 word；本批停在該入口。

所以零值路徑接完整 14 筆迴圈後，條件性 A0 仍為 **P−52**，不多扣 wrapper 已釋放的 32 bytes。非零值的低 byte 如何被 16DAC 使用屬既有後繼分析，不能在本批把 256、257 等任意 word 當成合法索引或事件成功。

## reply 與保存 word 的區分

1,560 組原始 selector 案例為兩個 wrapper × 260 個 word × helper reply={0,1,FFFFFFFF}。260 個 word 包含全部 byte，加 256、257、80000001、FFFFFFFF；高位非零而低 byte=0 的值仍走非零分支。

另 12,480 組在 helper 入口後明示改寫保存 word：兩個 wrapper × 8 個原 word × 260 個新 word × 3 個 helper reply。後續必須採新 word，不採 helper reply 或原暫存器 snapshot。

這些保存槽改寫只是合成條件，目的是區分 caller 實際讀取的值；不是觀察到 1070A 會修改此 word，也不證明實際 helper 已返回或維持 frame。沒有把「正常返回」推成「無副作用」。

## 重現與結果

[test_v4160_filter_callers_cpu.py](test_v4160_filter_callers_cpu.py) 使用原 APP、已發布的同目錄 CPU／work112 測試依賴與 18BA2 靜態 checker；只需標準庫，無 SDK carrier 或網路依賴。

```text
python analysis/test_v4160_filter_callers_cpu.py
python -O analysis/test_v4160_filter_callers_cpu.py

PASS: 3 raw direct-transfer candidates; 8 scanner controls; 1024 complete zero14 loops; static18ba2 contract applied without execution
PASS: 1560 original saved-selector cases; 12480 explicit saved-word rereads; exact single scale1 record and restored tail frames
PASS: 4 specified mutations; conditional pointer returns; 1070a/16c72/16dac and MMIO body NOT executed
```

一般與 `-O` 均通過，使用 `check()`。四個記憶體副本 mutation 改 14 筆上限、迴圈 mode byte offset、單筆 scale byte offset、wrapper 重讀保存槽的 offset；各自命中特定 context／ordered-access 檢查，不接受任意解碼或 unmapped 例外當作偵測。原 BIN 未修改。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 129C4..12A08 | `49fd66d87e515662bf6ca2a0cbb8f256d1769bac13947036df0ea3f8129f8b02` |
| 12A6E..12AA0 | `d146e7a9b7cf81686db54dedcba0bd151aaf55ce352b8f1a3bf0d7ffd44b6930` |
| 12AA0..12ABE | `115336cfb90f5472331cb914f71267fcb5295fb5518c1d669f557b673a17d2e9` |

後續仍需追查 1070A 的實際返回與保存合約、16C72 等後繼、上游 caller 與間接轉移，以及獨立 provider 的 installed 綁定。本批沒有操作實機 MMIO、IRQ、傳輸或啟動流程。
