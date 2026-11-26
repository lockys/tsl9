# v4.1.60：1070A 三次查表未命中的原指令返回鏈

2026-11-26。接續 [filter caller 與 selector 重讀](v4160-filter-callers-cpu.zh-TW.md)，本批把原 `1070A` 本機流程接入兩個 wrapper，取代上一批對整段 helper 的任意回傳值假設；fill provider 仍只採明示返回／目的效果。

原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 [保存槽靜態說明](v4160-selector-save-no-match.zh-TW.md) 已描述一條條件性未命中路徑，本批補原指令執行、精確存取及真正 wrapper 串接。未改既有 C、共享 CPU、原 BIN、seal 或 C 覆蓋率。

全部是有限 CPU 與合成記憶體。兩次 fill 不執行 provider；`9AF0` 的零旗標停在 `9AF6`，尚未執行 MMIO arm 的第一條指令；查表命中停在 `90CC`，尚未讀 payload、free 或 event target。沒有設備／MMIO／實際傳輸操作。

## 三鍵未命中時的完整本機順序

令 helper 入口 SP=W，nominal GP=20004000，callback table T=`2000be08`。本批路徑要求表內 15 個 `row+4` word 均不等於 `1061C`、`9B36`、`107C0`，且沒有外部干擾改表。

| 階段 | 原指令核對結果 |
|---|---|
| 1070A→10032 | 保存 caller RA 後，10032 讀 `[40048]` 並尾跳，參數 `(GP+300,0,3)`，RA=10712。 |
| 10712→1061C | 原 APP 直接寫 `U8[2000bfb8]=0`，計算 key=1061C，尾跳 90B0；其 RA=10718。 |
| 第一次 90B0 | 讀完 15 個 key，未命中自然返回 1；沒有列相關服務或表寫入。 |
| 10718→第二次 fill | 重新讀 `[40048]`，參數 `(2000bfb8,0,12)`，RA=1072C。 |
| 1072C→9AF0 | 實際讀 U8[GP+168]；非零跳至 RET 返回，零值停在本批 MMIO 邊界。 |
| 10730→第二次 90B0 | 計算 key=9B36、RA=1073C，未命中自然返回 1。 |
| 1073C→最後尾跳 | 先恢復 helper 的 RA、SP，再以 key=107C0 尾跳 90B0，第三次未命中直接返回外層 caller。 |

兩次 fill 的正常返回保存 live S、GP/SP、saved frame 與指定以外的合成記憶體，並允許破壞 A/T。每次分別採有／無目的填零效果；hook 不執行 provider code，也不證明 installed provider 真的只寫這些地址。額外 MMIO、alias、IRQ 或非正常返回不在此結果中。

第一個目的範圍為 `[2000412c,2000412f)`，第二個為 `[2000bfb8,2000bfc4)`，均與 table 及合成 stack 分離。1061C 的首 byte store 是原 APP 動作，與 hook 注入的填零分開核對；第二次 fill 無效果時，仍只有原 APP 清掉的首 byte 為零，其後 11 bytes 保留 fixture 原值。

在上述條件成立時，最後 A0 **固定為 1**，來自第三次原查表的未命中返回；不是最後 fill 的 reply，也不代表取消成功、硬體已生效或事件已執行。三次查表 key、15 列的 key 讀取順序、RA/SP/S 保存與全部映射記憶體寫入範圍皆逐段核對。

## 表不必全零，三次不必各自重新假設

288 組完整 helper 案例組合四種無匹配表、兩個 fill 各自有／無目的效果、三組 fill reply、flag={1,128,255}、slot target 固定／替換。

四種表包括 key 全零、非零高位 key、三個目標 key 的奇數鄰值，以及切換最高 bit 的完整 word；列的其他 bytes 與 payload 保留非零資料。90B0 比較完整原始 key，不把 bit0 正規化後再匹配。

同一份表經原三次掃描，沒有在中間清表或重設 fixture。原未命中查表只讀 15 個 `row+4`；固定區寫入、兩次限定目的 hook 及非零旗標分支均不改表，所以第一個未命中後，可沿這條有界路徑繼續核對原表。全 180-byte table 與兩側 canary 在返回時仍與入口一致。

另在第一次 fill 返回後替換合成 `[40048]` target，確認第二次 fill 使用新讀值；此為載入時機測試，不聲稱 installed slot 會變動。

## 巢狀 SP 並非三次相同

helper 自己保存 RA 在 W−4；前兩次查表都在 helper 的 16-byte frame 內，第三次則在恢復該 frame 後才尾跳。

| 查表時機 | 90B0 入口 SP | S0／S1／RA 保存位置 |
|---|---|---|
| 第一、第二次 | W−16 | W−24、W−28、W−20。 |
| 最後尾跳 | W | W−8、W−12、W−4。 |

最後一次會重用 helper 的舊 RA 槽，但保存的是已恢復的同一 caller RA。不能把三次都當成同一組 nested frame。

兩個 wrapper 保存 selector 的位址都是 **W+12**，不在上述 stack stores、table 或限定 fill 目的內。模型沿用既有高位合成 stack，不藉此宣稱實機 RAM 範圍、有效 stack placement 或實體 alias 已證明。

## 旗標與命中邊界

256 組獨立原 `9AF0` 案例覆蓋全部 byte：0 停在 9AF6；1..255 自然返回。兩種情形只改 A5 為讀到的 byte，其他 GPR 與映射記憶體保持入口值。

另有四組完整 cleanup 零旗標前綴，涵蓋兩個 fill 各自有／無效果。它們完成第一個未命中查表後，在 9AF6 停止，沒有繼續第二、第三次查表，也沒有宣稱完整 helper 返回。

90 個命中案例是**獨立查表邊界**控制：三個 key × 15 個位置 × payload={0,FFFFFFFF}，不從整個 cleanup 入口執行。即使該列 byte0 為零，也會依 `row+4` 匹配；本批一律停在 90CC，尚未讀 `row+8`，不執行 free／event 或修改命中列。它們用來確認「三鍵皆不在表」是閉合路徑的前提，沒有替完整命中流程背書。

## 實際 helper 接回兩個 selector wrapper

2,080 組為兩個 wrapper × 260 個完整 selector word × 兩次 fill 各自有／無效果。260 個值包含全部 byte，以及 256、257、80000001、FFFFFFFF；表內容、旗標與 slot 變化亦隨 fixture 改變。

每組實際執行 wrapper 前綴→1070A→10032／1061C／三次 90B0／非零旗標 9AF0，再回到原 selector reload；不再把整段 1070A 用 reply hook 略過。

- `12A6E` 從保存槽重讀原 selector。零值接單筆 18BA2 記錄入口；若另採已驗證的靜態正常返回合約，原 epilogue 返回舊記錄指標 P−36。非零停在 16C72，仍保留 wrapper frame。
- `12AA0` 重讀原 selector，恢復 RA/SP 後尾跳。零值接完整 129C4 的 14 筆 caller 迴圈，MMIO 仍只採靜態返回合約，最後為 P−52；非零停在 16DAC。

在本批無匹配、保存條件與範圍分離的 fixture 下，selector 保存 word 確實保持入口值。這比上一批明示改寫保存槽的 counterexample 更窄、更具體；不能外推為命中路徑、任意 provider 副作用或實際設備都保存它。

## 重現與結果

[test_v4160_cleanup1070a_cpu.py](test_v4160_cleanup1070a_cpu.py) 只需標準庫、原 APP 與已發布的同目錄測試依賴，不需 SDK carrier 或網路。

```text
python analysis/test_v4160_cleanup1070a_cpu.py
python -O analysis/test_v4160_cleanup1070a_cpu.py

PASS: 288 complete1070a no-match cases; 3 real15-row scans/case; return1; two explicit fill effects/returns
PASS: 256 guarded flag bytes; 4 full zero-flag prefixes stopped before MMIO; 90 table-hit boundaries stopped before payload/free/event
PASS: 2080 actual-wrapper chains preserve saved selector; 6 specified mutations; provider/MMIO bodies NOT executed
```

一般及 `-O` 均通過，使用 `check()`。六個記憶體副本 mutation 改第一／第二 fill count、最後 key、查表 miss 返回值、helper frame 恢復量、旗標 branch polarity；各自命中特定參數／context／result 檢查，不接受任意 exception 當作成功。branch mutation 也仍在 9AF6 停住，沒有因 mutant 進入 MMIO arm。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 1070A..1074C | `bfaf48119b3e1a2a47c8c6e926a7dcbe8e04d09da21ceab042f6a353bfe9499d` |
| 10032..10044 | `19fdb01a67f9a747ed26411c6b72994155e02050b531c4b22f57d80bf8f25878` |
| 1061C..10630 | `f274d15ad8921781d519c0757976841267827eaee180fcbb02f4b794f0ece0ca` |
| 90B0..9124 | `6ae3c32faae25ccd27fea46de4a04b6246489daafb5f1fa0d9ede512e65f2b31` |
| 9AF0..9B02 | `062e0f7c892fef6208cbfa5739947ac7249170e022cbb000bde3b7ce17cb0340` |

最後一列 hash 固定包含完整原函式，但本批執行範圍刻意排除 9AF6..9B00，亦不對該 MMIO arm 注入可執行模型。

後續仍需釐清 table 命中時的 payload／free／event 合約、旗標零分支的靜態 MMIO 意圖、其他上層 caller 及 installed provider 身分。完整實機啟動、IRQ、硬體與傳輸相容仍未證。
