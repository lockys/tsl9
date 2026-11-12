# V4.1.60 0x167a6 first-loop candidate

固定參考基準 `d6e2391030eee86cc73426c206c47c7750e00c57`；image `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，image base `0x8000`。固定的連續指令視窗 `[0x167a6,0x167de)` 為：

```text
01 11 22 cc 26 ca 4a c8 4e c6 06 ce 52 c4 56 c2
 aa 84 01 44 93 89 01 06 13 09 e0 0f 83 a7 09 00
 a2 97 03 c7 07 00 63 16 97 00 03 c5 17 00 ef e0
 df df 09 04 e3 14 24 ff
```

## 抽象邊界

只模型 first loop：每次透過 snapshot callback 取得 pointer slot 的當前值，對該 snapshot 讀 key offset 0,2,...,252；key 作無號 byte 擴展後與完整 `uint32_t` event 比較。相等時以同一 snapshot 讀 offset+1，再 dispatch 該 byte；不提早退出。callbacks 可改變 slot、表內容及其他狀態，讀 value 時不快照內容。下一次迭代重新 snapshot。原視窗的 slot 為 GP+96，呼叫目標為 0x155d0；本介面不綁定這些位址。

呼叫者負責有效的 callbacks/context、snapshot 的生命週期和各次讀取的定義；callbacks 必須正常返回，且執行期間 callback 結構須保持有效及不變。模型不假設 pointer 有效、表實際存在或動態可用、可達性、並行安全、後續 loop、dispatch 內部行為或其他記憶體操作。這不是 ABI、機器碼或全函式等價聲明。

## 離線驗證

```text
python -I -S -B experiments/v4160-167a6-first-loop-candidate/verify.py
python -I -S -B -O experiments/v4160-167a6-first-loop-candidate/verify.py
```

驗證整個 image hash/長度、視窗 bytes 及 C/header 的精確 SHA-256，並測試修改、截斷；Python synthetic trace 測試 key callback 更換 slot 和修改 value、dispatch 更換 slot、重複命中、value 高位、首次 snapshot 與末次 dispatch 的狀態變化、所有 byte events 和大於 255 的完整輸入。unittest 在 `-O` 下仍檢查。這是靜態 pin 和 Python 模型自檢，C/hash 固定不等於語義驗證；不執行或驗證 C 與 Python 一致，也不是 ISA 模擬、target differential 或硬體證明；不使用 compiler、target、simulator、network 或設定。
