# V4.1.60 BT KeyBoard 資料格式分支：有界靜態逆向

本元件是 callback 中的**資料格式分支**，範圍從 `0x11cdc` 的 s4 檢查至共同入口 `0x11c64` 或拒絕出口 `0x1240c`；不是完整 callback，也不是已確認的鍵盤協定。原始映像為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，映射基址 0x8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。原始指令此前已有機械式重建；本輪補上先前局部報告未分析的長度 5 和 2 分支語意。

**入口假設**：上游 `[s6]` 間接呼叫已正常返回非零；s4、s3、s2 的值與指標可用。slot 真實目標未知，無法確定該呼叫是否是名稱比較，也不證明實際可達性。令 p=s3 指向的 bytes、q=s2 指向的 bytes；下列按原始指令靜態推導，假設讀取有效：

| s4 | 接受條件 | 32-bit 值 V |
|---|---|---|
| 8 | p[1], p[3..7] 均為零 | q[0]:q[1]:p[0]:p[2] |
| 5 | p[0] 非零且 p[1..4] 均為零 | q[0]:q[1]:q[2]:p[0] |
| 2 | p[1] 無號值不大於 2 | q[0]:q[1]:q[2]:((p[0]+p[1]) mod 256) |
| 其他 | 拒絕 | 無 |

冒號表示由高至低的 byte；輸入 V=0 時 8、2 走拒絕出口，而 5 已由 p[0] 非零保證 V 非零。成功抵達 `0x11c64`；拒絕抵達 `0x1240c`。此切片沒有 store 或呼叫，後續共同路徑和未知呼叫**不在元件行為範圍**。指標/記憶體有效性、對應事件用途、上游呼叫和下游副作用均未由此證明。

分支證據、bytes、解碼邊界與模型限制見 [s4=8](../tsl9-bt-keyboard-local/README.md)、[s4=5](../tsl9-bt-keyboard-s4-5/README.zh-TW.md)、[s4=2](../tsl9-bt-keyboard-s4-two/README.md)。這些證據包含原始映像固定 hash、選定機器碼及分支目標；資料流部分使用既有指令清單判讀，不是完整獨立反組譯。模型測試是依靜態理解編寫的合約，不是固件執行、硬體或獨立動態確認。

重現（由 repo 根目錄）：

```sh
python -B -m unittest discover -s experiments/tsl9-bt-keyboard-local -v
python -B -m unittest discover -s experiments/tsl9-bt-keyboard-s4-5 -v
python -B -m unittest discover -s experiments/tsl9-bt-keyboard-s4-two -v
python -B -m unittest discover -s experiments/tsl9-bt-keyboard-normalizer -v
```

未執行韌體或操作硬體，沒有據此宣稱 OTA、最終連結或可燒錄映像已完成。
