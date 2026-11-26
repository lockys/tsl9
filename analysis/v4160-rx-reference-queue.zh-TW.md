# v4.1.60 RX、copy 參考與佇列槽位的原指令串接

2026-11-26。使用既有本機 v4.1.60 APP 與 V1.31 SDK copy reference，未下載資料、未操作設備。APP SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；carrier 與 58-byte helper 的身分固定方式同[上一批參考驗證](v4160-reference-copy-cpu.zh-TW.md)。設備安裝的 provider 身分仍未知。

## 新串接的範圍

從 `0x16a7c` 執行接收取樣、`0x16896` 傳輸原指令，再通過 RX guard、`0x12bc8` producer，呼叫指定 SDK 參考的原始 58-byte copy body，執行 producer 的 tag 寫入與接收函式完整返回。全部使用同一組合成記憶體／暫存器，只有 STATUS／DATA 輸入與初始 row／stack／slot／MMIO fixture 為合成資料。

不是以前的 one-byte copy stub，也沒有用主機 memcpy 補 payload。指定參考 binding 不證明設備採用它；loader 沒有執行，`FENCE.I` 仍只核對編碼並記錄事件，不模擬 cache／硬體效果。

## 正常槽位的順序

producer 找到首 halfword 為零的槽位後，原指令順序是：

1. `0x12bf6` 寫 ID halfword。
2. `0x12bfa` 寫長度 byte。
3. fresh-load `[0x4004c]`，呼叫參考 target；其參數是 `(slot+3, capture_frame+21, length)`。
4. 參考 body 保存／清零控制 word、記錄 FENCE、逐 byte 複製指定 prefix，正常返回前恢復控制 word。
5. **copy 正常返回後**，`0x12c0e` 才寫入 tag 到 `slot+11`。

RX 已將完整長度限制為 1–8，故參考 body 只改寫 `slot+3..+10` 中的指定 prefix，未用的尾部保持舊值。逐例比對整個 384-byte queue、精確 queue store 順序、所有 reference read/write/FENCE 事件、控制 word 及接收 caller 的 RA/SP/S0–S2 恢復。

## 零 ID、重用與滿佇列

ID 零仍可正常複製 payload 和更新 tag，但首 halfword 保持零。以原 consumer ID guard 重讀該槽 snapshot，會在 `0x12c94` 跳往 `0x12cee`；下一個 producer 仍可選同槽。32 個槽各做一次後續非零 ID、不同長度／payload／tag 的插入，確認重用結果及未覆寫的尾部。

滿佇列時 producer 不呼叫參考 body、不寫 queue、不產生 reference MMIO 效果，然後正常返回接收 caller。沒有把這個結果擴大成佇列的全域並行性或設備行為。

## 部分 copy 中止的 snapshot

對 ID 零與 ID 325 各模擬第三次 payload store 中止：

- ID 與長度已寫入，前兩個 payload bytes 已完成。
- 第三個與剩餘 payload bytes 保持舊值，舊 tag 未被更新。
- reference 控制 word 保持零，沒有補造 restore、producer tag store 或 caller return。

在停止後，對實際 queue snapshot 獨立執行 consumer 的 ID guard：零 ID 跳過，非零 ID 通過。只跑至分支結果，**不執行 CSR 或消費操作**。後面槽位直接以 S0 指定目標槽，不是從 consumer 入口完整掃描到那一槽。因此這不是實際 IRQ 競爭、原子性或 consumer 必定看到半寫入資料的證據。

## 重現與結果

```powershell
python analysis/test_v4160_rx_reference_queue.py
python -O analysis/test_v4160_rx_reference_queue.py
```

需要標準庫、原 APP、已發布的同目錄測試依賴，以及既有 V1.31 carrier；可用 `--carrier <path>` 指定相同雜湊的檔案，不自動下載。

```text
PASS: 4096 RX/reference/slot/tag cases; 45 zero/timeout substitutions; 4 full queues; 32 zero-ID reuses; 2 interrupted snapshots; tag mutation detected; installed binding UNPROVED
```

4,096 組為八個 ID 邊界（含 0）× 八個有效長度 × 32 個首空槽 × tag 1／2，沒有宣稱枚舉所有 ID。45 組將 15 次取樣呼叫之一分別替成成功零／第一階段逾時／第二階段逾時，仍執行原傳輸指令並核對返回／取樣次數／DATA 存取差異。長度變零者由 guard 拒絕，標頭／payload 變零則依實際合成 frame 重新判斷。

另測 4 組滿佇列、32 組零 ID 重用與兩個部分中止 snapshot。記憶體複本把 tag store 從 `slot+11` 改成 `slot+10`，必須被精確 store 順序檢查抓出；原始 APP／carrier 未改。一般與 `-O` 均通過，上一批獨立 copy／TX 參考檢查也重跑通過。

本批只新增此腳本與報告，未修改共用解譯器或前批證據。上批歷史封存重播的 README drift 仍未解，也未宣稱 loader／舊 seal 重播通過。沒有新增 C/C++ 重建 bytes 或重算覆蓋率；實際 provider、外設、中斷與硬體相容仍未證。
