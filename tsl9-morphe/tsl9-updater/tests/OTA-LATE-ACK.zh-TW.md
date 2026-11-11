# 遲到 W ACK：部分離線實驗

`OtaLateAckProtocolTests.java` 使用實際 `OtaSession` 和 `Protocol.encode/Decoder`，以合成 frame 分片注入；listener、連線與 callback 是測試替身，**不是實際 `BleClient`**。無硬體或網路操作，也未修改正式傳輸語義。

事件順序：舊輪 W0 成功、W1 本地 callback、斷線（session 失敗）、新輪 U/S 完成、送 W0；此時注入假設的舊 W1 回覆 `00`。在新 W0 callback 之前注入時，回覆先被緩存，callback 後新輪即送 W1；在 callback 之後注入則立即送 W1。這重現的是 **session 在此假設回覆下的誤進度**，並未證明真實跨連線封包可抵達。

合成完整 W1 echo 的前兩 byte 是 `00 01`，新輪等待 W0 時會拒絕並重試 W0；完整 W0 echo 則接受，因此即使回覆攜頁，同頁跨輪仍不可區分。單 byte `00` 沒有頁識別，空回覆也沒有頁識別，實際 session 對空回覆重試。這些是測試輸入與現有解析器行為，**不是觀察到的設備回覆**。

實際回覆格式尚未驗證：現有 [ID2580 BOOT 靜態分析](../../../analysis/boot2580-ota-page-conflicts/README.md) 僅顯示相符後請求空 W 回覆，且不能證明 BLE 封包送達或與 ID2966 配對。不能據此宣稱 `00` 或完整 echo 是該設備真實 ACK。`BleClient.close()` 清除 decoder、佇列並更換 GATT，notification 亦檢查 GATT 身分；本實驗沒有在純 JVM 執行實際 Android `BleClient`，因此無法判定舊連線 callback/notification 能否跨越這些邊界，也無法排除同一連線重試的遲到回覆。需要 Android API 測試替身或可執行的 JVM transport seam，以及具來源的真實封包或更完整的設備回覆靜態證據；不能為測試假設而改產品語義。

從 repo 根目錄執行（Python 3、JDK）：

```sh
python -c "import tempfile,subprocess,pathlib; r=pathlib.Path.cwd(); s=r/'tsl9-morphe/tsl9-updater/app/src/main/java/dev/tsl9/morphe'; t=r/'tsl9-morphe/tsl9-updater/tests/OtaLateAckProtocolTests.java'; d=tempfile.TemporaryDirectory(); subprocess.run(['javac','-encoding','UTF-8','-d',d.name,*[str(s/(x+'.java')) for x in ['FirmwareImage','OtaSession','Protocol','UiMessage','UiException']],str(t)],check=True); subprocess.run(['java','-cp',d.name,'dev.tsl9.morphe.OtaLateAckProtocolTests'],check=True)"
```

本機執行 PASS；尚未接入完整測試套件。
