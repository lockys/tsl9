# W 中斷後的主機契約（純 JVM）

原始 TX alternative 的 76,800 bytes 與本機參考逐 byte 相同，但其建置依賴 opaque 原始載體及完整參考；不認證來源、不證明可開機或可刷寫（[證據](../../../analysis/original-tx-alternative-NOT-FLASH-VALIDATED.md)）。[全映像分析](../../../analysis/ota-full-image-offline-contract.md) 的分頁/envelope 是合成資料；保存的 ID2580 BOOT 靜態 W 數值範圍不是 ID2966 實機配對或 Flash 物理行為。斷線可能發生於擦除、寫入、ACK、E 或重啟之間；主機不知道頁面是否已提交，byte 相同及 W ACK 都無法保證電源中斷恢復。既有 [頁測試](OTA-PAGE-RANGE.zh-TW.md) 的同步 callback 沒覆蓋此交錯。

本測試選擇一個較窄契約：第二頁 W 已交給 transport，但本地 callback 和設備 ACK 均尚未交付時斷線；主機必須失敗而非宣稱完成，舊 callback/ACK 在失敗狀態無效；使用者明確重新 start 後從第 0 頁重送，而非推測續傳。最後 E 回覆前不成功。使用兩頁合成資料、虛擬時鐘和記憶體 listener，直接執行實際 `OtaSession`，不模擬 BOOT/Flash，不修改正式傳輸語義。重新開始後只注入舊 callback，**不假設舊同命令 ACK 可被辨識**：協定無會話 ID，遲到的 W ACK 若恰逢新 W 仍可能被誤認；此測試不證明隔離該情況。

從 repo 根目錄，需 Python 3 和 JDK：

```sh
python -c "import tempfile,subprocess,pathlib; r=pathlib.Path.cwd(); s=r/'tsl9-morphe/tsl9-updater/app/src/main/java/dev/tsl9/morphe'; t=r/'tsl9-morphe/tsl9-updater/tests/OtaInterruptedWriteTests.java'; d=tempfile.TemporaryDirectory(); subprocess.run(['javac','-encoding','UTF-8','-d',d.name,*[str(s/(x+'.java')) for x in ['FirmwareImage','OtaSession','Protocol','UiMessage','UiException']],str(t)],check=True); subprocess.run(['java','-cp',d.name,'dev.tsl9.morphe.OtaInterruptedWriteTests'],check=True)"
```

亦已接入 `test.ps1`。本機獨立測試 PASS；完整 `test.ps1` 在此測試 PASS 後因缺少 `tsl9-morphe/artifacts/firmware-trace/miniapp/app-service.js` 而停止，不能宣稱整套通過。E 回覆後此測試的 `success` 只是現有主機狀態，無 readback，不能證明實際寫入、重新啟動或恢復；重送是否安全／冪等、已提交頁狀態、BOOT 身分、物理斷電及其他交錯均未驗證。未連設備。
