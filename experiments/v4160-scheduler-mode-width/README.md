# 排程器 mode 位寬的受限指令軌跡

對固定 v4.1.60 原始 BIN，以固定指令表執行從 `0x920e` 選定空槽後到 `0x91e8` 居民路徑選擇的片段。假設先前掃描選到空槽、輸入延遲非零；**不執行掃描、居民函式或實機**。

合成反例：index 0、callback `0x1333c`、delay 300 時，mode `0` 與 `0x100` 存入的 mode byte 都是 `0`，但前者選 `0x922c`、後者選 `0x91ea`；mask 為 1、換算值為 480。這是完整 32 位 mode 比較與低 8 位儲存的差異，不表示真實呼叫者曾傳入 `0x100` 或排程成功。

`verify.py` 執行 1,920 個合成軌跡，涵蓋 15 槽、多種 mode、延遲環繞和 task 值，並拒絕 18 個指令編碼變造。此處為既有指令的行為測試，不是新增原始 byte 覆蓋。

`model.c` 是選定空槽後的 C 語意投影；`differential.py` 的 C11、C++17 各 67,456 組與固定指令表比對，包含所有低 16 位 mode 值及四種語意變造。輸入 index 限制為 0–14，delay 非零；不執行實際讀寫或掃描。

```text
python -I -B experiments/v4160-scheduler-mode-width/verify.py
python -I -B experiments/v4160-scheduler-mode-width/differential.py --vcvars <vcvars64.bat>
```
