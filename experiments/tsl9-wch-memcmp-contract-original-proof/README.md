# WCH 比較函式候選位元組檢查

對兩份公開 WCH resident 候選 carrier 的 72-byte 比較函式，檢查完整 carrier SHA-256、片段雜湊、23 條指令邊界及五個分支的暫存器與相對目標。兩版的 flash 偏移不同，但所記錄的目標 RAM 位址相同。缺少本機候選 carrier 時會明確標示 SKIP，只檢查內建的紀錄位元組；存在但雜湊不符則失敗。

```text
python -I -B experiments/tsl9-wch-memcmp-contract-original-proof/verify.py
```

此檢查不是對 TSL9 實際安裝的 ROM 取樣；`9422` 僅依既有資料紀錄為條件性 Xwchc 指令位元組，並未驗證裝置 ISA 或執行行為。也未證明整體 C 模型、ABI、中斷安全或硬體行為。
