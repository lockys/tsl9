# BLE generation、隊列與遲到 ACK：靜態追蹤及有界離線測試

範圍：目前工作樹的 `app/src/main/java/dev/tsl9/morphe/BleClient.java`、`OtaSession.java`、`Protocol.java`。以下是源碼可見的防護，不是 Android 或外設實測；未連接設備、未刷寫、未改正式傳輸策略。

## 靜態證據

- `connect()` 先 `close()`；後者遞增 `epoch`，設 CLOSED、清 `busy`、`current`、寫入/資訊讀取隊列、characteristic、decoder，將 `gatt` 設 null 後 disconnect/close 舊物件。連線、寫入及資訊讀取的延遲 timeout 使用 epoch；GATT callback 經 main handler 派送後比對當前 `gatt` 物件。這對不同 GATT 物件的舊 callback（包含已排入 handler 者）提供隔離；不是對封包來源或重用同一物件的通用 generation 證明。
- `writeNext()` 同時只持有一個 `current`，逐 chunk 設 `busy`；成功 write callback 才發下個 chunk，最後 callback 後才執行 `done`。`close()` 清掉待寫及 current，不主動執行其 `done`。callback 的條件是 GATT 身分、busy、current 非 null、UUID 為 DATA，**沒有 chunk/attempt token 或 characteristic 物件身分比對**；timeout 使用 epoch、current 物件和 offset。這不證明 Android 實際會重複或延遲派送相同 GATT 的 write callback。
- notification 的兩個 API 路徑複製 bytes 後 post；`notifyValue()` 只檢查 GATT 身分及 DATA UUID，不檢查 READY、寫入狀態、epoch 或 OTA attempt。它先呼叫 `events.notification`，再把 bytes 餵 decoder，將完整 frame 交給 `events.packet`。close 重置 decoder；同一 GATT 內的舊 notification 沒有來源/請求識別。
- `OtaSession.transmit()` 為每次嘗試遞增 `sequence`，closure 檢查 token 和 active，排除舊嘗試的本地完成 callback；符合 command 的早到 packet 只緩存第一個，完成 callback 後處理。這個 token **不在收到的 packet 中**。W 接受單 byte `00` 或當前完整 page；前者不能識別頁或嘗試。timeout 後重試仍使用同一 command/payload，同頁完整 echo 亦不能區分前次嘗試。空回覆在現行程式重試。
- 寫入逾時會 `problem()` → `close()`；OTA ACK 逾時則由 `OtaSession.tick()` 重試，不必然關閉 GATT。上述推論依賴呼叫方確實在同一連線持續 tick 和路由 packet，並非真機時序證明。

## 可執行合成排程

`OtaSameConnectionLateAckTests.java` 重用 `OtaLateAckProtocolTests` 的實際 session、frame codec、分片 decoder 和假 listener/時鐘：W0 callback 後將時鐘精確推到 1200ms，tick 觸發 W0 retry；舊 closure 被忽略；假設一個 `00` 在 retry callback 前或後到達，然後假設另一個 W0 `00` 在 W1 callback 後到達。兩個排程均觀察到 W1 被接受、進入 END。測試固定兩頁、兩種排程、無睡眠／網路／硬體。它展示解析器對**注入的**無頁識別回覆不可區分，而不是證明真機會產生兩個 `00`、會延遲或重複封包，亦不是 BleClient/GATT 測試。原 `OTA-LATE-ACK.zh-TW.md` 包含跨 session 的相應假設及回覆格式證據限制。

從 repo 根目錄執行（Python 3、JDK）：

```sh
python -c "import tempfile,subprocess,pathlib; r=pathlib.Path.cwd(); p=r/'tsl9-morphe/tsl9-updater'; s=p/'app/src/main/java/dev/tsl9/morphe'; t=p/'tests'; d=tempfile.TemporaryDirectory(); subprocess.run(['javac','-encoding','UTF-8','-d',d.name,*[str(s/(x+'.java')) for x in ['FirmwareImage','OtaSession','Protocol','UiMessage','UiException']],str(t/'OtaLateAckProtocolTests.java'),str(t/'OtaSameConnectionLateAckTests.java')],check=True); subprocess.run(['java','-cp',d.name,'dev.tsl9.morphe.OtaSameConnectionLateAckTests'],check=True)"
```

## 尚未執行的 Android 邊界測試設計

現有 `app/src/androidTest/java/dev/tsl9/morphe/BleQueueChecks.java` 只在 closed 狀態反射測試 queue pruner，不提供可控 GATT 或 callback 排程。可在 Android 測試建立隔離的可控 GATT 替身和 main-looper 排程（或先設計不改策略的注入 seam），在不呼叫實際 `connectGatt`、不掃描的前提下：

1. 舊 GATT 上排入 partial notification、write callback 和 timeout，close 後建立不同的新 GATT；依次排放舊事件，斷言不產生 packet、不完成新 current、不斷開新連線；再送新 GATT 的完整 frame 驗證 decoder 沒有串接舊 partial。
2. 新 GATT 上測不同 UUID、無 busy/current 的 callback 均忽略；逐 chunk callback 驗證一次只發一塊、完成後才執行 done，close 清 pending 且不執行 done。
3. 同 GATT 的合成重複 callback／遲到 notification 分開測試：記錄現有行為而不假定平台保證；結合 session 的早/晚 ACK 測試，不能把模擬行為當真機觀測。所有事件以手動 drain looper 和有限 timeout 驗證，避免睡眠及無限等待。

這些 Android 案例**僅為設計，尚未實作或執行**。設備 ACK 格式、真實 Android callback 排序/重複與跨連線送達仍未知，需有來源的封包及平台/真機證據才能評估策略；不建議由此合成實驗直接修改 OTA 策略。
