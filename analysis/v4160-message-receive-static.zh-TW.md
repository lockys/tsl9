# 訊息取出、marker 還原與內部指標釋放：離線靜態合約

接續 [threshold 訊息建立／入佇列](v4160-threshold-message-static.zh-TW.md)，本輪展開 SDK `tmos_msg_receive` 對應的兩個參考候選完整本體，接回已驗證 APP task 與 resident kind1 handler。原始目標仍為 ID-2966 V4.1.60 APP，76,800B，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 新增的完整本體

| 本體 | V1.31 | V1.40 | 各版本 bytes／指令 |
| --- | --- | --- | --- |
| receive | RAM `0x2000028C`，來源 `0x404FC` | RAM `0x2000028C`，來源 `0x4053C` | 136B／50i |
| unlink | `0x4319C` | `0x43228` | 30B／10i |

合計四個完整候選本體 **332B／120 指令**。SDK raw header 的 JT14 對應 slot `0x4006C`，兩候選該 slot 均為 `0x2000028C`；候選的 first-copy 座標涵蓋完整 receive。這些是靜態候選映射，**不是原機 installed provider 證明**。receive 有一條掃描 backedge；unlink 本機 CFG 無環且不呼叫任何服務。

## receive：選第一筆，查看第二筆

入口 full task 保存在 S2，queue head slot 為 `0x20003198`／`0x200031E8`，與前輪 sender 相同。receive 沒有自己的 task-count 或 task>2 檢查，而是比較每個 message 的 fresh unsigned byte `M-2` 與完整 task 值。因此大於 255 的 task 不會符合任一 U8 marker；不能把 sender 的輸入限制當成 receive 已執行的檢查。

掃描過程中，S1 初值為 0，保存第一筆 matching M；A2 在第一筆 match 之前，隨 mismatch 更新為前一節點，第一筆 match 之後不再更新。掃描持續到第二筆 match 或 null，再作以下選擇：

| 找到同 task 訊息的數量 | 本機後續 | 正常返回 |
| --- | --- | --- |
| 0 | `stop_task(task,0x8000)` | 0 |
| 1 | unlink 第一筆，再 `stop_task(task,0x8000)` | 第一筆 M |
| 至少 2 | unlink 第一筆，再 `event(task,0x8000)` | 第一筆 M |

receive 的三個 mapped calls 分別是 `0x439A8`／`0x43A34` 的 **完整 stop-task wrapper**、本輪 unlink、`0x4354A`／`0x435D6` 的 event helper。stop-task 還包含 timer lookup／mask 與條件 return-mask 處理，不能簡稱成「只清一個 pending bit」。本輪重用 [既有 stop-task 合約](v4160-cancel-provider-static.json)；正常返回、S／SP／RA 與 saved-frame 保存、存取有效與 nonalias 仍是串接前提。

stop／event 的 scalar 回覆均未被 receive 檢查；末端先 `A0=live S1`，再從 frame 還原入口 S1。因此在 context 保存條件下，返回的是被選中的 M 或 0，不是 callee status。鏈表有限且穩定時，最多比較原鏈表長度 n 次 marker；若較早找到第二筆 match，便提早離開。未證明實際鏈表有限、無環或沒有並行寫入。

## unlink：摘除但不 free

參數為 A0=head slot pointer、A1=selected M、A2=selected predecessor。unlink 重新讀取 head 與 `U32[M-8]`：

- fresh head==M：把 M 的 next 發布為新 head。
- 否則：把 M 的 next 寫到 predecessor-8；這需要 predecessor 正確且仍有效，函式不自行驗證 membership。
- 隨後寫 `U32[M-8]=0`、`U8[M-2]=255`，再返回。

unlink 只寫 head／predecessor link、被取出訊息的 next 與 marker；沒有讀寫四-byte body，沒有 free／callback／event 呼叫，只有 A4／A5 被定義。不同節點、head slot、frame、header 與 globals 的有效分離仍需證據。marker 重設為 255 後，才可能通過 public deallocator 的 marker guard；單純被摘除不等於已經釋放。

## APP 與 registered handler 的後續

重用原始 APP task `0x17476..0x174EE` 的 120B／43i，與兩候選既有 kind1 handler 的各 130B 本體。其 bit15 路徑均為：

```text
receive(task)
  返回 0：略過 deallocate
  返回 nonzero M：deallocate(M)
以保存的完整 event E XOR 0x8000 返回
```

這兩處在 receive 與 deallocate 之間均沒有解讀 M 的四-byte body。即使 receive 為 0，或 cleanup 沒有真正釋放，仍會在 context 保存／正常返回條件下移除本次返回值的 bit15。這不是硬體事件送達或排程器正確重投遞的證明。APP task 與 resident kind1 是不同入口的替代性串接，尚未證明原機實際採用哪一條。

## 補上 M 內部指標可釋放原區塊的條件性證明

前輪已確認 public deallocator 會把 **M 原值**送到 private release `0x20000110`，而 M 不等於 core payload Q。本輪進一步沿 private release 的完整原指令核對：它先沿 heap header 鏈表找含輸入指標的範圍，再從選中的 **header+4／+6** 讀 size／tag，並非將 M-8 直接當成 private header。

對既有 nominal heap 前提，取：

| 記號 | 位址／角色 |
| --- | --- |
| H | `0x200043AC`，原始 free block，payload size 504 |
| Q | H+8=`0x200043B4`，core payload |
| M | H+16=`0x200043BC`，四-byte message |
| R | H+20=`0x200043C0`，切分後 remainder header |
| B | `0x200045AC`，原 next／large-head 邊界 |

core request=12、tag=`0xF004` 時，`504 = 12 + 8 + 484`；R 的 free payload size 為 484。`H <= M <= R` 且 `M >= H+8`，所以 M 與 Q 通過相同的前綴 range guards，仍選中 H。之後 private release 不再用原輸入值來定位 header；清 H 的 tag，與仍 free 的 R 合併，恢復 H.size=504、H.next=B。account 的 `-20 + 12 + 8` 在全部 65,536 個 U16 值下恢復原值。

wrapper、builder、sender、append、unlink 對這筆 message 的本機 prefix／body／marker／next 寫入，均位於 `[H+8,R)`，不碰 H 或 R 的 private headers。checker 另以不可變區間算式核對此點。其他節點的寫入、stop-task 的 timer 存取、事件資料、frame、control word 與全域 account 仍需 nonalias 與保存條件。

因此，**在明列的 nominal 配置／header／全域／無干擾前提下，可證明 M 也釋放同一個原區塊 H**，補上前輪未完成的配對。這不是任意 interior pointer 都有效的保證，也不是實際裝置 heap／ownership 已證。selected private release stores 沒有抹掉四-byte body；free 後殘存 bytes 不表示仍有權存取或使用該物件。

## 驗證與剩餘工作

[checker](check_v4160_message_receive_static.py) · [精確 ledger](v4160-message-receive-static.json)

```powershell
python -B analysis/check_v4160_message_receive_static.py
python -O -B analysis/check_v4160_message_receive_static.py
```

每條新指令各一個變異，共 **120** 個，另有 **2** 個 marker LBU→LB 變異。每版本核對長度 0～8 的 **511** 個不可變 matching-position 模式，共 1,022 條語法 CFG 見證，涵蓋 receive 全部本機邊；這是分支／位置證明，不是可變 queue 或 ISA 模擬，也沒有把所有模式宣稱成真實可達輸入。另重用既有 APP、SDK、private allocation／release、sender 與 handler 的完整 bytes／operand guards。

普通與 `-O` 模式均須與 ledger 逐 byte 相符；APP、兩份 candidate、SDK raw header 與 Xwchc 來源向量均固定。未執行原韌體、target ISA、provider、callback、heap／queue 模型或 MMIO，未操作硬體。GitHub 僅新增本輪三份分析檔。實際 provider、登錄／派送順序、其他 consumers、所有 writers／保存期與物理事件進展仍未完成；C 重建覆蓋率不因本輪改變。
