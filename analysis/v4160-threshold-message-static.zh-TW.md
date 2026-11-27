# threshold helper、四位元組訊息與入佇列：原指令靜態合約

本輪接續 [record／node 保存期](v4160-record-node-lifecycle-static.zh-TW.md)，展開 RAM callback 的 threshold 出口所呼叫服務。兩份 resident 仍只是 V1.31／V1.40 **參考候選**，沒有證明是原機 installed provider。原始 APP 為 ID-2966 V4.1.60、76,800B，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 本輪範圍

| 完整本體 | V1.31 | V1.40 | 各版本 bytes／指令 |
| --- | --- | --- | --- |
| threshold helper | `0x568F6` | `0x56A36` | 124B／42i |
| 四-byte builder | `0x5E3A8` | `0x5E4F0` | 102B／39i |
| message sender | `0x43208` | `0x43294` | 146B／50i |
| queue append | RAM `0x2000021C`，來源 `0x4048C` | RAM `0x2000021C`，來源 `0x404CC` | 26B／10i |

合計八個完整候選本體 **796B／282 指令**，含固定 operand、bytes hash、所有本機 CFG 邊的語法見證；不是 C 重建覆蓋增加量。只有 append 有鏈表迴圈，其餘三本體的本機 CFG 無環；未知 callee／鏈表的真正終止性仍未證。

## threshold 的零返回不代表訊息送達

以 helper 入口 A0 的物件為 O、A1 為 reason。以下物件語義需要 nested callees 保持 S0／S1、SP 與有效 frame；到達最後原始 `LI A0,0; ...; RET` 本身可直接證明 A0=0。

1. 先取樣全域 owner word；若等於入口 O，先清零。之後才進入訊息服務。
2. `U32[O+288] != 0` 時提出 `(fresh U16[O+8],128,0)`；這個 word 是分支條件，沒有將它當 pointer 解參考。
3. 再取樣 `U16[O+68]`；非零時提出 `(fresh U16[O+8],129,19)`。
4. 一律提出 `(fresh U16[O+8],129,5)`。三次 key 都是重新讀取，不能假定相等。
5. 寫 byte `O+10=0`、`O+16=0`、`O+84=low8(reason)`。較晚取樣的全域 status 若為 5，另寫零。
6. 正常走到末端時，A0 **固定為 0**，不檢查任何 builder 回覆。A1 沒有保存／還原，不能宣稱返回時仍是 8 或 129。

全域 status 的取樣早於上述物件 stores。若物件與全域、T、frame 有 alias，後續 store 可能改變先前欄位，不能把取樣值當作清除當下的 fresh 值。292-byte 有效、適當對齊的 O 範圍是涵蓋本體存取的充分界限，並非已證明的真實配置大小。

## builder 與四個 bytes 的來源

builder 保存入口 ID／code／reason，呼叫既有 RAM allocator `0x20000236`，要求可見長度 4。若 allocator 返回 0，builder 還原 frame，返回 **4**。若得到 M，寫入：

| 位移 | 內容 |
| --- | --- |
| M+0 | low8(code)：128 或 129 |
| M+1 | low8(reason)：0、19 或 5 |
| M+2～3 | 取樣 ID 的 low16，小端序 |

四個可見 bytes 均由本體初始化。之後重新讀取 candidate 的 task byte，還原自己的 frame／S registers／RA，**無新 link 尾跳**到 sender；成功分支沒有自己的固定成功碼，而是由 sender 決定返回值。

沿用已驗證 allocator 合約：原始 private header 為 H，core payload Q=H+8；要求 core 的大小為 12、tag 為 `0xF004`。wrapper 初始化 Q+0～3 的 next=0、Q+4～5 的 length=4、Q+6 的 marker=255，**Q+7 未初始化**。可見 M=Q+8=H+16，四-byte body 結束於 H+20；不把全部 12-byte payload 宣稱成已初始化。

allocator 與 core 的 failure 前綴沒有寫 A2，故 optional fallback 可看到當時的 reason。若其 fresh failure slot 非零，core 邊界為 `(A0=1,A1=0x000CF004,A2=then-live reason)`；hook 的身分、副作用、保存期仍未知。這與其他使用同一 slot 的 ABI 不可混為一談。

## sender 入佇列、事件回覆與清理界線

sender 對 nonnull M 要求：完整 task 值大於 2，且小於重新讀取的 unsigned task-count byte；然後要求 `U32[M-8]==0`、`U8[M-2]==255`。全部成立時：

1. 將 M-2 的 marker 改成 low8(task)。在 count 為 U8 的前提下，可接受 task 為 3～254。
2. 呼叫 append，將 heap message M 發布至 candidate 全域 head（`0x20003198`／`0x200031E8`）。保存的是 M，沒有將 builder 的 SP 暫存位址當作訊息 body。
3. 呼叫 event helper `(task,0x8000)`，之後不檢查回覆，固定返回 **0**。event helper 另一次 fresh count 可能已改變，因此入佇列成功與事件送達不是同一保證。

nonnull 的無效 task 會嘗試 deallocate，再返回 **3**；無效 header 也嘗試 deallocate，再返回 **5**；null M 直接返回 **5**。這些 sender 碼不取決於清理服務回覆。

**本輪核對出的重要界線：** public deallocator 通過 marker==255 後，把 **M 原值**傳給 private release `0x20000110`，沒有減 8。M=H+16 與原本的 core payload Q=H+8 不同，不能把先前針對精確 payload Q 的 allocation／free 逆運算證明套在此處，也不能宣稱 sender 的失敗路徑已成功釋放原區塊。marker 不符時，更可能根本沒有 private release 呼叫。

append 先清 `M-8`，再讀 head；空佇列直接發布，非空時沿既有 message 的 `-8` next 欄位找尾再接上。需要有限、有效的鏈表，以及尚未入列的獨立 M。它沒有 duplicate／cycle 檢查；不能宣稱 polling 進展或完整 message consume／free 保存期已完成。這條 message queue 與前輪 record-node 的 `+12` next 不是同一結構。

## 接回 RAM callback 的兩種出口

兩候選的 mapped callback 入口均為 `0x20000D50`。重用已封存的 52B threshold 出口及 20B ordinary epilogue：出口先令 A1=8、A0=then-live S0，呼叫本輪 helper；再把返回 A0 的 low8 存到 then-live S0+43，然後 **fresh 讀取 T**（`0x20003220`／`0x20003270`）。

- 若 helper 正常返回且 frame／SP／物件與還原值保持有效，可串接 `O+43=0`；helper 的 `O+84=8` 另需其 S1／S0 及後續 alias 保存條件。
- fresh T==0 時，ordinary epilogue 還原 frame 後以 **A0=0** 返回；A1 是 then-live 值，沒有固定為 8。
- fresh T!=0 時，還原 frame，令 **A0=5、A1=2**，無新 link 地 `JR(T & ~1)`。這是尾移交，不能叫作「普通返回 5」；raw T=1 甚至會導向有效位址 0。

callback 入口 T=0 不足以證明這次 fresh 讀取仍為 0。物件 byte43、helper 物件／frame、allocator／deallocator、queue、event 與 control stores 都需有效 nonalias 及保存條件；另須排除 IRQ／DMA／重入／其他 writers。本輪沒有把 control-word stores／`FENCE.I` 解釋成已證明的實體 critical section。

## 重播與限制

[靜態 checker](check_v4160_threshold_message_static.py) 與 [精確 ledger](v4160-threshold-message-static.json) 可在根目錄重播：

```powershell
python -B analysis/check_v4160_threshold_message_static.py
python -O -B analysis/check_v4160_threshold_message_static.py
```

每個完整本體的每條原指令都有單點變異拒絕，共 **282**；另有 **8** 個 unsigned→signed 編碼變異，特別覆蓋 threshold LHU、builder task LBU、sender count／marker LBU。純整數資料域核對 65,536 組 task／count（31,878 組可接受）與 196,608 組四-byte payload。

兩模式均須與同一 ledger 逐 byte 相符，並核對 APP、兩份候選、SDK raw header 與既存 Xwchc 來源向量。分析未執行 target ISA、原韌體、callback、provider、MMIO 或 heap／list 模型，未操作硬體。GitHub 僅發布這三份新分析檔，原 BIN 與既有工作保留。實際 provider 綁定、message 消費與釋放保存期、完整 T 保存證明仍待追查；95.75% C 重建快照不因本輪而提高。
