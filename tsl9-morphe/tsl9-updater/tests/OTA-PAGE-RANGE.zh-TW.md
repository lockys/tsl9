# 離線 OTA 頁範圍檢查

`OtaPageRangeTests.java` 直接編譯目前的 `FirmwareImage`、`OtaSession`、`Protocol`；listener 只保存在記憶體，回覆與時鐘均為測試輸入，沒有 BLE 或硬體操作。從 repository 根目錄執行（需 Python 3 與 JDK）：

```sh
python -c "import tempfile,subprocess,pathlib; r=pathlib.Path.cwd(); s=r/'tsl9-morphe/tsl9-updater/app/src/main/java/dev/tsl9/morphe'; t=r/'tsl9-morphe/tsl9-updater/tests/OtaPageRangeTests.java'; img=r/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'; d=tempfile.TemporaryDirectory(); subprocess.run(['javac','-d',d.name,*[str(s/(x+'.java')) for x in ['FirmwareImage','OtaSession','Protocol','UiMessage','UiException']],str(t)],check=True); subprocess.run(['java','-cp',d.name,'dev.tsl9.morphe.OtaPageRangeTests',str(img)],check=True)"
```

* 官方原始檔 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，76,800 bytes = 75 × 1024；RAW 模式實際 W 頁索引 **0–74**，每個 W payload 1026 bytes（兩 byte 大端索引及 1024 bytes 資料），逐頁比對來源。不是 75–95。啟用 readback 時 R 請求 0–74，另發一個索引 75 的 R（16 bytes），不是額外 W；該尾端 R 回覆內容不檢查，再進入 E。未啟用 readback 則直接 E。
* 少一 byte 的 RAW、1025-byte PAGED、錯誤 PAGED 索引被拒；明確選擇 RAW_FF_PAD 才補 `ff`。但整頁截斷成 74 頁會被接受且只送 0–73；加長至 96／97 頁也會被接受並分別送 0–95／0–96。這些是現況，不是安全驗證或建議傳送。解析器不知道預期 ID2966 長度，不能從整頁對齊推斷完整性。
* 偽回覆檢查 W 無效短回覆與逾時重送同頁、最多 9 次發送；R 短回覆重送相同請求、最多 5 次發送後失敗。正向測試使用合成 W 成功與 R 逐頁回覆；不代表設備接受或成功寫入。傳輸回調均同步完成，沒有覆蓋全部非同步交錯。
* 先前 [ID2580 BOOT 數值範圍](../../../analysis/boot2580-w-range-2026-11-01/README.md) 在其明列前提下得到 W 索引 0–95 通過，目的數值範圍涵蓋 page 75–95；這是另一個 BOOT 映像的靜態條件算術，不是實際 Flash 幾何。ID2966 正常檔不會 W 到那些頁；延長檔則本 updater 會送到該處，97 頁亦會送 96，是否被設備拒絕未測。

**無法證明 ID2580 BOOT 與 ID2966 配對或安裝於同一設備。** 此測試不證明真實 BOOT 身分、實際接收／擦除／寫入、電源中斷恢復或新 runtime 啟動；不能把測試成功當成可刷寫證明。
