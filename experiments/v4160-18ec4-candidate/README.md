# 0x18ec4 event-bus 候選

`candidate.c` 是依相鄰 `../v4160-18ec4-evidence/README.md` 的固定映像靜態指令語意所寫的小型 ISO C 候選。固定映像 SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；視窗 SHA-256 為 `40e81eda78577543dd451a59487376d58352cb623c796194e0fcc9c12b23995d`。這些 hash 固定身分，並不證明來源。

介面使用 context 與 32-bit read/write callbacks 表示抽象事件，不是目標 ABI，也不是純 C target 證明。使用前提是每次呼叫的函數指標有效且型別相符，context 及回呼所用共享物件在使用時具有效生命週期，且不存在資料競爭或其他未定義行為；假設 callbacks 正常返回。重入本身可發生，但呼叫端仍須維持這些前提。回呼可能令地址別名、改變共享狀態或影響後續讀取，因此三次 control read/write 保持獨立，中間有 address 寫入，poll 每次 fresh read 且無 timeout，返回 masked a0。callback 異常或不返回不在此假設內；status bit 持續為 1 會無限等待。實際 mapping、MMIO、硬體效果及終止性均未知。

`test_reference.py` 只執行獨立 Python reference 模型，核對精確事件 fixtures、別名、零值、多次 poll 與有限 busy 前綴觀察，並 pin `candidate.c` 的 SHA-256 身分。有限觀察中由測試中斷不證明真正不返回。Python **不執行或驗證 C**；source hash 只偵測位元組變動，不證明 C 正確。本模型不是固件模擬，也不是 target 執行或驗證。

離線驗證（不編譯或執行 C）：

```
python -B experiments/v4160-18ec4-candidate/test_reference.py
python -B -O experiments/v4160-18ec4-candidate/test_reference.py
```

本工作未編譯或執行 C、未執行或模擬 target，未使用網路、硬體或更改 settings。
