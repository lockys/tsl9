# v4.1.60：1070A 命中列、free／event 邊界與後續查表

2026-11-26。接續 [1070A 三次未命中鏈](v4160-cleanup1070a-cpu.zh-TW.md)，本批展開 `90B0` 第一筆 key 命中後的 payload、列清除、event 尾跳，並串回原 1070A 的三次查找與 selector wrapper。

原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 `src/native/receive/callback_table.c` 與 [callback closeout 驗證](v4160-callback-closeout-cpu.zh-TW.md) 已保存取消路徑；本批增加 free 返回後的精確後續、live 表格變化及完整 cleanup 串接，不重算 C 覆蓋率。

所有記憶體、slot 指標與服務結果都是離線 fixture。fill／free／event 均只停在入口並採明示返回條件，provider、MMIO、設備與實際事件操作未執行。free／event 名稱只識別現有槽位的呼叫角色，不證明實際服務身分、釋放成功或事件已取消。

## 第一個完整 key 命中與 payload

原 `90B0` 依序比較 15 個 `row+4` 的完整 word，命中第一筆即停止掃描，只讀該列 `row+8` 的完整 payload word。沒有先依 row byte0 篩選，也沒有將 key 的 bit0 正規化。

| payload | 原 APP 後續 |
|---|---|
| 完整 word=0 | 不讀 `[40068]`，直接進 `90E0` 的列清除／event 前綴。 |
| 任意非零 word | 讀 `[40068]` 並呼叫，以 A0=完整 payload，RA=90E0；返回後才進相同前綴。 |

360 組匹配案例覆蓋全部 15 列 × payload={0,1,80000000,FFFFFFFF} × event reply={0,1,FFFFFFFF} × free 後 hook 有／無。高位非零但低 byte 為零的 payload 也會進 free 邊界。

非零 payload 的 free 入口仍在 16-byte nested frame 內：live S0=index、S1=table base、GP/SP 與 saved caller frame 都還會被後續使用。測試明示 free 正常返回，保存這些 live context，破壞 A/T 並提供一個與後續 task byte 無關的 reply；沒有執行 free 本體或把物件當作真的已釋放。

## free 返回後不重讀 key／payload

令 90B0 入口 SP=P，命中列號 i，table=`2000be08`。從原 `90E0` 起的精確順序為：

1. 依 live S0 計算 `12*i` 與 `(1 << i)`。
2. 從 P−8 恢復 caller S0，從 P−4 恢復 caller RA。
3. **重新讀** U8[GP+166] 作 task byte。
4. 依 live S1 table base 加偏移，寫零到該列 +4、+8。
5. **重新讀** `[4005c]` 作 event target。
6. 從 P−12 恢復 caller S1、SP 回到 P，尾跳該 target。

free 之後沒有再讀列內 key 或 payload，也沒有檢查 free reply。測試在 free 邊界後明示改寫當前列的 key／payload，原碼仍清掉同一 index 的這兩個 word；它沒有改用新 key 再查一次。

兩組負向保存控制分別破壞 live S0 與 S1，讓原碼改算另一個有效列。指定 ordered-access 檢查必須拒絕；不以 unmapped 例外充當偵測。這說明 saved caller S0/S1 之後會恢復，不代表 free 可在返回前任意破壞其 live 值。

共享 CPU 未實作此處 RV32 variable SLL。新測試只在 `90E8` 固定精確 word `008595b3`，按 RV32 shift-count 低 5 bits 處理該單一指令，再回到未更動的共享解碼器；不是新增一般指令支援或執行 provider。

## event 尾跳與新讀值

在 `[4005c]` 入口，原取消函式已恢復 caller frame：

```text
RA = 原 caller resume
SP = 90B0 入口 SP
A0 = 最新 U8[GP+166]
A1 = 1 << index，index=0..14
caller S0/S1 已恢復
```

1,024 組 task 案例覆蓋全部 256 個 byte × index={0,14} × payload={0,FFFFFFFF}。非零 payload 在 free 返回前把 task byte 改成下一個 byte，確認 event 使用新讀值；另有 free 後替換 event slot target 的案例。

列 key／payload 的清零在 event target 讀取及呼叫之前已完成。event 回覆本身不控制原取消函式是否清列；在本批 event 保存記憶體的返回前提下，reply=FFFFFFFF 也不會由原 caller 回滾那些 stores。這不等於證明實際 event 服務沒有其他副作用。

event 尾跳正常返回至原 resume PC 是明示前提；它需要保存 caller S、GP/SP 與 saved frame。RA 暫存器本身與 A/T 在返回 fixture 中可破壞，不能把尾跳當成還有一層本機取消 frame 尚待恢復。

## 三個 key 分別看當下的表格

1,620 組完整 1070A 鏈為：15 組循環排列的不同列位置 × 三個 key 各取 {未命中、零 payload 命中、非零 payload 命中} 的 27 種組合 × 最後 event reply={0,FFFFFFFF} × 兩次 fill 皆有／皆無目的效果。

fill 與 event／free 的保存條件沿用明示前提；GP+168 固定非零，仍停避 9AF0 的 MMIO arm。兩次 fill 只注入目的區效果，不執行服務，也不在每次查找前重建或清空 table。

原三個查找 key 仍依序是 1061C、9B36、107C0。第一、第二次查找在 cleanup 的 frame 內；最後一次在恢復 cleanup SP／RA 後尾跳。每次都重新掃描當時 table，命中列清除後才往後繼續。

額外合成條件核對三種跨查找行為：

- 同一 key 在兩列重複時，只處理較早那一列；另一列保留，因這個 key 不會在本次 cleanup 再掃第二次。
- 第一個 event 返回後明示加入第二個 key，再於第二個 event 返回後加入第三個 key；後續兩次原查找必須命中新加入列。
- 第一個 event 返回後明示移除原有第三個 key，最後查找必須走未命中。

這些插入／移除都是 host hook，用來驗證後續讀取時機，不是觀察到的 provider 行為或並行安全保證。當前列 free 後修改與後續列 event 後修改也分開記錄，沒有把所有服務副作用混成一份入口 snapshot。

## 最後返回值由第三次決定

在本批正常返回與保存條件下：

| 第三次查找結果 | 1070A 的最後 A0 |
|---|---|
| 未命中 | 原 90B0 自然返回的 1。 |
| 命中，不需 free | 最後 event 的明示完整 reply。 |
| 命中，先呼叫 free | 最後 event 的明示完整 reply；free reply 不取代它。 |

前兩次 event 的不同 reply 被後續流程覆寫，沒有被累積成成功／失敗碼。第三個 key 被 hook 移除的案例，即使第一個 event reply=0，最後也因 miss 得到 1。

540 組實際 wrapper 鏈覆蓋 `12A6E`／`12AA0` × selector={0,1,256,257,FFFFFFFF} × 27 種三鍵狀態 × 最後 event reply={0,FFFFFFFF}。原 wrapper 先進真正 1070A，再從原保存槽重讀完整 selector，仍不依 cleanup A0 選路。

wrapper 只接至原後繼入口：12A6E 零值到單筆 18BA2、非零到 16C72；12AA0 零值尾跳 129C4、非零尾跳 16DAC。這些後繼本體在本批均不執行。

## 重現與結果

[test_v4160_cleanup_hits_cpu.py](test_v4160_cleanup_hits_cpu.py) 使用原 APP、已發布的同目錄 CPU 測試依賴與標準庫，沒有 SDK carrier 或網路依賴。未更改既有 C、共享 CPU、原 BIN、seal，也未增加 C 覆蓋率。

```text
python analysis/test_v4160_cleanup_hits_cpu.py
python -O analysis/test_v4160_cleanup_hits_cpu.py

PASS: 360 matched-row/free/event cases; 1024 task-byte probes; two live S0/S1 preservation controls
PASS: 1620 three-key cleanup chains; 540 wrapper reload chains; first duplicate only; explicit later-key insertion/deletion
PASS: 4 specified mutations; free/event/fill returns explicit; provider/MMIO bodies NOT executed
```

一般及 `-O` 均通過，使用 `check()`。四個記憶體副本 mutation 改 payload load offset、key clear offset、task byte offset、event slot offset。每個要求命中特定 ordered-access guard，不接受任意解碼／unmapped 例外。突變路徑也預先停在已知的合成 provider 邊界，沒有嘗試執行 provider target。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 90B0..90E0 | `44d0ab1fa200379759353c4dea1ca2fb575e1af3ebdc5fce046a268bd413ecc6` |
| 90E0..9110 | `673e6887bbaf419ffea8b64382396df1d04448e682eab72541463f26facf902b` |
| 9110..9124 | `3a7b4661fb975b2106431af5303cc6fb771ccadfd1e94800a06a8e559e7303a0` |
| 1070A..1074C | `bfaf48119b3e1a2a47c8c6e926a7dcbe8e04d09da21ceab042f6a353bfe9499d` |

後續仍需釐清 `[40068]`／`[4005c]` 的實際綁定與保存／記憶體合約、其他上層 caller，以及 9AF0 零旗標 arm 的靜態 MMIO 意圖。這批不證明真實釋放、事件、IRQ 或設備執行結果。
