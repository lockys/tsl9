# 排程器 mode 位寬的受限指令軌跡

對固定 v4.1.60 原始 BIN，以固定指令表執行從 `0x920e` 選定空槽後到 `0x91e8` 居民路徑選擇的片段。假設先前掃描選到空槽、輸入延遲非零；**不執行掃描、居民函式或實機**。

合成反例：index 0、callback `0x1333c`、delay 300 時，mode `0` 與 `0x100` 存入的 mode byte 都是 `0`，但前者選 `0x922c`、後者選 `0x91ea`；mask 為 1、換算值為 480。這是完整 32 位 mode 比較與低 8 位儲存的差異，不表示真實呼叫者曾傳入 `0x100` 或排程成功。

`verify.py` 執行 1,920 個合成軌跡，涵蓋 15 槽、多種 mode、延遲環繞和 task 值，並拒絕 18 個指令編碼變造。此處為既有指令的行為測試，不是新增原始 byte 覆蓋。

`free_scan.py` 另從 `0x9206` 執行固定指令表：假設前一輪比對未命中、`a5=0x2000be08` 且讀取成功且穩定，依序讀 15 筆的 `+4` word，選第一個零；全非零則在 `0x9234` 前得到 `a0=1`。窮舉 32,768 種佔用組合，將 32,767 個選槽結果接到後段投影，並拒絕 9 個指令變造。組合只檢查片段邊界，沒有執行前一輪掃描或證明輸入可達；尤其 callback 為零且有空槽時，不可假定前輪會未命中。

`match_scan.py` 模擬非零延遲入口的前一輪 callback 比對（`0x9196` 至命中或 `0x9206`），保持 `a5` 指向表首。98,304 組位元圖及 19,683 組混合表確認第一個相等項目優先於空槽；在穩定讀取下，callback 為零時只有全非零表才能未命中並進入空槽掃描。這是兩段投影的合成組合，不含命中後動作、其他入口或實機。

`match_update.py` 模擬命中後 `0x91a2–0x91d0`：先讀選中項目 `+8`，非零則以該值呼叫 `[0x40068]`；接著讀 `gp+166`，寫入 mode 低 byte 與新的 `+8` word，並產生索引 mask。片段沒有明示寫入 callback word，但 provider 可能有未知副作用，因此不能保證它未改變。1,800 組合成軌跡、6,000 組掃描接續及 16 個指令變造；provider 僅假定正常返回及保存必要暫存器，不證 target 有效或硬體行為。

`match_model.c` 是命中更新的 C 語意投影；`match_differential.py` 比對原指令軌跡，C11/C++17 各 85,536 組及四種語意變造。涵蓋全部低 16 位 mode，但不是 mode、索引與舊參數的完整笛卡兒積。Provider 副作用不在投影中。

`zero_delay_scan.py` 驗證零延遲時先掃 15 個槽位：32,768 種佔用組合與 8 種指令變造；若全滿會落到一般路徑，並非直接證明返回失敗。`zero_delay_insert.py` 再以 10,000 組合成軌跡接續首個空槽，記錄 callback word、零 mode byte、參數 word 寫入及從 `[0x40050]` 載入尾跳目標；21 種指令變造被拒。堆疊與其他讀取值由測試直接提供，未模擬記憶體別名、provider 或硬體。

`zero_delay_model.c` 將零延遲插入後的明示事件、保存暫存器與尾跳參數還原為 C 投影。`zero_delay_differential.py` 各以 C11/C++17 比對 30,000 個合成軌跡，含堆疊指標模 2³² 環繞，並拒絕四種 C 語意變造；讀取值獨立提供，不模擬別名或 trap。

`model.c` 是選定空槽後的 C 語意投影；`differential.py` 的 C11、C++17 各 67,456 組與固定指令表比對，包含所有低 16 位 mode 值及四種語意變造。輸入 index 限制為 0–14，delay 非零；不執行實際讀寫或掃描。

```text
python -I -B experiments/v4160-scheduler-mode-width/verify.py
python -I -B experiments/v4160-scheduler-mode-width/free_scan.py
python -I -B experiments/v4160-scheduler-mode-width/match_scan.py
python -I -B experiments/v4160-scheduler-mode-width/match_update.py
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_scan.py
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_insert.py
python -I -B experiments/v4160-scheduler-mode-width/zero_delay_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/match_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-scheduler-mode-width/differential.py --vcvars <vcvars64.bat>
```
