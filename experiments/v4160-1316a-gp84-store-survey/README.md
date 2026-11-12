# V4.1.60 GP+84 store 原始模式調查

`scan.py` 對本地 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 驗證長度 76,800 與完整 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，以基址 `0x8000` 映射完整 image。逐個偶數檔案 offset 掃描完整 4-byte little-endian 視窗，不假設指令邊界，解碼標準 S-type SB/SH/SW、rs1=x3、12-bit sign-extended immediate；只列出寫入 byte 區間與 GP 相對 `[84,88)` 相交的所有精確 bitpattern。資料或其他指令的中間 bytes 亦可能是候選，不代表可執行或可達。

本次固定 image 結果：**零筆候選**。這不是全域 writer 的證明，無法排除 compressed 或其他編碼、其他暫存器形成的 GP alias、間接寫入、bulk copy、runtime 變化或其他 image/provider。既有 reset 分析的 GP 初始值 `0x20004000` 只是條件式初始值，不是 runtime guard，也不保證 `0x1316a` 路徑執行時 GP 或 RAM 狀態。此為純靜態 byte survey，未執行或模擬 firmware。

```sh
python -I -S -B experiments/v4160-1316a-gp84-store-survey/scan.py
python -B experiments/v4160-1316a-gp84-store-survey/test_scan.py
python -B -O experiments/v4160-1316a-gp84-store-survey/test_scan.py
```

測試窮舉三種寬度的全部 4096 個有號 immediate（包含相交及兩側鄰界）、對齊、截斷、非匹配編碼和 image 突變；pin 檢查不依賴 `assert`。
