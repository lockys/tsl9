# WCH 比較函式候選位元組檢查

對兩份公開 WCH resident 候選 carrier 的 72-byte 比較函式，檢查完整 carrier SHA-256、片段雜湊、23 條指令邊界、五個分支的暫存器與相對目標，11 個標準 RV32 指令的操作數（含 MMIO 載入、清除、恢復和 byte 載入），以及六個壓縮指令的暫存器與立即值（含返回與遞增）。條件式 Xwchc 半字則依候選 WCH LLVM TableGen 的 `QK_C_LBU` 編碼解碼為 `a3, 0(a3)`；2,048 組欄位編碼／解碼與 16 個單位元變造檢查通過。兩版的 flash 偏移不同，但所記錄的目標 RAM 位址相同。缺少本機候選 carrier 時會明確標示 SKIP，只檢查內建的紀錄位元組；存在但雜湊不符則失敗。

```text
python -I -B experiments/tsl9-wch-memcmp-contract-original-proof/verify.py
python -I -B experiments/tsl9-wch-memcmp-contract-original-proof/differential.py --vcvars <vcvars64.bat>
```

`differential.py` 將原候選指令的固定 PC 語意投影與既有 C 模型比較：C11、C++17 各 20,000 組隨機合成軌跡，另有 2,304 組完整路徑（全部 byte 值與八個不相等位置及相等情況）和 484 組失敗／觀察上限組合，包含後端拒絕、觀察次數上限及條件式 Xwchc。五種 C 語意變造（返回值、讀取來源、profile 閘門、恢復位置、遞增量）均被差分比較拒絕。投影不是通用指令解碼器；當 profile 啟用時假設 `0x2294` 是 `lbu a3,0(a3)`，未啟用時於該指令前停止。

此檢查不是對 TSL9 實際安裝的 ROM 取樣；`9422` 的解碼依賴既有候選 Xwchc TableGen profile，並未驗證裝置 ISA 或執行行為；編碼與解碼皆由同一規格轉寫，並非獨立硬體驗證。差分測試不證明所有可能情況的 C 模型、ABI、中斷安全或硬體行為。
