# v4.1.60：外層 event dispatcher 的完整雙版本靜態合約

日期：2026-11-26。接續 [linked-node consumer](v4160-linked-node-consumer-static.zh-TW.md)，固定外層函式的全部原指令、條件性 CFG、stores 與 maintenance→consumer 的直接邊。[檢查器](check_v4160_event_dispatch_static.py)／[ledger](v4160-event-dispatch-static.json) 保存可重播證據。

既有 [Task 3 交付與合併](v4160-task3-dispatch-and-rearm.zh-TW.md) 已描述 V1.31 的局部流程。本輪增量是兩版完整本體、每條 opcode/operand/target guards、RAM 執行座標、完整 stores census、與前輪 consumer／post-config 的顯式槽位串接。**仍未證明實際 installed provider、事件成功送達、物件 ownership 或保存期。**

全程只讀本機 bytes、解碼指令及驗算主機整數；沒有執行或模擬 target ISA、scheduler、pending table、node list、provider、callback、allocator 或 MMIO。未修改原 BIN 或既有 ledger；C 重建覆蓋率不增加。

## 完整範圍

所有 range 終點不含在內；下表位址為十六進位。

| 候選 | flash load-image source | first-copy 對應 RAM | SHA-256 |
| --- | --- | --- | --- |
| V1.31 | `40a40..40bf6` | `200007d0..20000986` | `bd63b35b352cf367a879d5d7c282905295538eaa7b18b16d294765447cbe0a40` |
| V1.40 | `40a80..40c36` | `200007d0..20000986` | `ad64465c017cf16b6e1b0c5d6dbb27567cfce78ef64d96171cd52f69f5d478e1` |

每版 **438 bytes、150 instructions、18 個靜態 store 位址**；兩版合計 **876 bytes、300 instructions、36 stores**。每版含 7 個 frame stores；不是執行次數。32-byte frame 保存 RA、S0..S5。全部 150 條指令分界及操作數均固定，其中 AUIPC/JALR pair 另按 runtime PC 解算。正常返回前提下的 CFG 覆蓋全部指令，另明列唯一外部 tail edge，不把它當成普通 RET。

固定 raw SDK header 把 `TMOS_SystemProcess` 寫為 `BLE_LIB_RAM_JT(0)`。這是 API alias 證據，**尚未證明 RAM JT0 的啟動寫入來源、執行時 word 等於本函式，或 v4.1.60 實際綁定**。候選 first-copy 的完整來源範圍與映射沿用既有 checker；第二段 sparse copy 的末端缺口仍保留，沒有補零。

## globals 與直接呼叫

M 為 metadata base；下列加數為十進位。

| 角色 | V1.31 | V1.40 |
| --- | --- | --- |
| cursor：U8[M] | `2000319c` | `200031ec` |
| count：U8[M+1] | `2000319d` | `200031ed` |
| handler-table pointer：M+40 | `200031c4` | `20003214` |
| optional hook：M+44 | `200031c8` | `20003218` |
| return-mask halfword：M+64 | `200031dc` | `2000322c` |
| time-like provider：M+68 | `200031e0` | `20003230` |
| pending-table pointer：M+72 | `200031e4` | `20003234` |
| B=M+152 | `20003234` | `20003284` |
| F=M+888 | `20003514` | `20003564` |

M+40、M+72、M+1 與 [post-config](v4160-post-config-static.zh-TW.md) 的 table/event/count storage slot 逐項核對；slot 相同不代表不同時間的 live pointer、count 或內容相同。

| runtime transfer PC | 類型／目標 |
| --- | --- |
| `20000812`、`200008cc` | 兩條 call，V1.31→`20002610`，V1.40→`2000265c`；opaque |
| `20000818` | 無本機 null guard 的 hook call |
| `2000081e` | 另一個有本機 null check 的 hook call |
| `20000872` | 直接 call linked-node consumer `200004fa`，link=`20000874` |
| `200008be` | 還原 frame 後 tail→`2000061a`，不是 RET |
| `2000090a` | 無 null guard 的 handler call，link=`2000090c` |
| `2000093c` | optional M+44 hook call |
| `20000972` | AUIPC/JALR，V1.31→`63dd0`，V1.40→`63eba`；opaque |

PC-relative 指令全部依 RAM PC 解讀，不沿用 flash load-image 反組譯的 target。所有 opaque call 的正常返回只是 CFG 前提，沒有證明其副作用、context 保存、終止或實際可呼叫。

## scan：先讀 pending，再比 bounds

入口先經 B/F 相關 byte gates、直接 opaque callee 與 hooks，才讀 P0=U32[M+72]、count0=U8[M+1]。scan 每次讀 cursor=i_probe，**在 bounds 比較之前**先讀 U16[P0+2*i_probe]。

- probe 值為零：cursor=(i_probe+1)&255，寫回 U8[M]；若結果<count0 就繼續 scan，否則轉到後續 bounds 分支。
- probe 值非零：重新讀 cursor=i_bound；只有 i_bound<count0 才進入交付，否則先把 cursor 清零再進 maintenance。

這裡沒有對第一次 pending load 的本機 bounds guard，count=0 也不能用來推導「不會讀 table」。U8 cursor 會回繞；有效 extent、count/cursor 保存、nonalias、外部 writer 與終止都需另外證據。

## snapshot、clear、call：三個 cursor 身分不能自動合併

以下 offsets 相對 runtime 入口 `200007d0`，以十六進位表示：

1. `+114..+118` 使用當時 i_bound 與先前 P0，**重新讀一次**選定半字至 A1=E。這是第二次 pending 讀取，可與 probe 不同，甚至為零。
2. `+11a` 把該半字全部清零。
3. `+11e` 再讀 cursor→A0=i_task；fresh 讀 U32[M+40]，取 U32[T+4*i_task] 為 handler pointer。
4. `+136` 清 U16[M+64]；`+13a` 間接 call handler，**沒有本機 null guard，也沒有對 i_task 再做一次 bounds test**。

因此入口參數是完整 A0=i_task（由 U8 讀值而來）、A1=E（由 U16 讀值而來）。不能直接指定固定 task ID、非零 E、單一事件 bit，或認定清槽與 handler table 使用同一筆 task。

## 返回後 merge 與 cursor／hook

handler 正常返回後，保留 full A0=R，fresh 讀 C=U16[M+64]、cursor=i_after、pending base=P1，最後 fresh 讀 H=U16[P1+2*i_after]：

```text
U16[P1+2*i_after] = low16(H | (R & ~C))
```

沒有把 P1、i_after 無條件當成 P0、i_task 或 i_bound。若地址／context 保存且讀寫間沒有其他 writer，H 中已重設的 bit 會由 OR 保留；即使 C 含某 bit，H 中該 bit 也不會被這次 merge 清掉。**不能推論這是 read-modify-write atomic 或能保住 H 讀取之後的非同步寫入**。M+64 的其他 writers 與完整語義仍待釐清，本文只按其 operand 用途稱 return mask。

merge 後再 fresh 讀 cursor=i_increment：零就保持零；非零才加一，以 SB 寫 low8。255 因此可回繞成零。接著 fresh 讀 M+44，非零才 call；正常返回後**無條件把 M+44 清零**，不能保證保留 hook 自己重寫的新值。再讀 cursor 與 count：cursor>=count 會走 reset/maintenance，否則進 epilogue；所以「每次呼叫只做一件事」也不是無條件合約。

## maintenance 到 linked-node consumer

scan 過界或返回後 bounds 分支可把 cursor 清零，再經 F+9 等 gate。當 fresh U32[M+68] 非零時：讀 fresh U32[B+4]，寫入 hint U32[M+16]，於 `20000872` 直接呼叫已驗證的 `200004fa` consumer。

正常返回位址是 `20000874`，後面繼續其他 provider／byte gates、可能的 pending scan／opaque tail 或 epilogue；**不直接回到本函式前段的事件交付 scan**。因此 consumer 設位不代表會在同一次外層呼叫內立即進 handler。M+68 gate 也沒有固定之後 callee 所讀到的 provider pointer，兩次讀值的保存仍是前提。

函式本身沒有包住整段的控制 word save/clear/FENCE.I 指令，不能據此證明外部呼叫者一定有或沒有保護；也不能從 event helper 內部的控制讀寫推論整段 dispatcher atomic。RET 路徑不統一設定 A0；另一條路徑 tail 交給 `2000061a`，返回合約未閉合。

## 與 builtin record handler 的實參串接

post-config 以當時 n／T 快照登記 literal0、literal1、literal1。若這些表項、cursor、pointer、count 都保持有效且選到該 task，dispatcher 傳入的是**絕對 task ID**，沒有減掉登記起點 n。

[literal0／literal1 合約](v4160-builtin-record-handlers-static.zh-TW.md) 把入口 A0=g 用於 `12*(16*g+k)` record 位址。因此 literal0 位於 task n 時，g=n，不自動等於零。literal0 返回前另讀的 fresh flag 使用 groupless k；callback record 與 flag record 不必同筆。只有 n=0 等額外條件成立，才能把前輪 producer 的首組 record 與這條派送連成同一筆。這裡仍沒有實際登記 n、event delivery 或 callback pointer 保存證據。

## 重播與發布範圍

必備本機輸入是固定 APP、兩份 reference-only carrier、raw SDK header、既有 LLVM Xwchc 來源與 vectors；transitive identity guards 固定全部身分。原 APP 為 76800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。候選輸入仍在 `analysis/wch-resident-candidate-2026-10-21/`，本輪不下載、不上傳；只有 GitHub clone 不足以完整重播。

檢查器另依賴 17 個既有本機 Python 檔，發布前逐一比對 GitHub main blob 身分。本輪只發布新 checker、ledger、本文；不改動原 BIN、既有分析、C 原始碼或本機 Git index。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_event_dispatch_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_event_dispatch_static.py
```

兩種模式重播同一 ledger；使用 RuntimeError guards，不依賴可被 `-O` 移除的 assert。主機驗證為 524288 個 merge identities、256 個 cursor cases，以及 17 個指定原指令單 bit 變異須在預期 operand guard 失敗。這不是 scheduler／event-memory／register machine 模型。

尚需追查 RAM JT0 的來源、實際 installed provider、登記 task/group、M+64 writers、各 opaque callee／tail、callback 重入與 node/record ownership。正常 callee-return、S/SP/frame 保存、有效 extent、無不利 alias、無未建模 writer/interrupt 等都保留為條件，不能提升成實機保證。
