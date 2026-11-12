# V4.1.60 BED5 有界原始寫入掃描

對應 `analysis/v4160-bed5-adjacent-store-survey.zh-TW.md`。輸入為固定 V4.1.60 decoded BIN，長度 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，以 `0x8000` 映射。輸入身分不符時拒絕執行。

從 repository 根目錄以隔離 Python 執行：

```
python -I -S -B experiments/v4160-main-bed5-raw-store-scan/scan.py
python -I -S -B experiments/v4160-main-bed5-raw-store-scan/test_scan.py
python -I -S -B -O experiments/v4160-main-bed5-raw-store-scan/test_scan.py
```

掃描每個偶數位移的原始半字起點，檢查相鄰 AUIPC/LUI + SB/SH/SW/C.SW 及獨立 x0-base SB/SH/SW。完整範圍及限制見分析文件：不證明指令邊界、可達性或全域寫入者完備；reset、非相鄰構址、間接指標與非同步等不在此模式內。`local_scan_complete` 僅指此語法模式窮舉完畢，`global_writer_complete` 固定為 false。
