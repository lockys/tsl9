# APK 1.2.7 OTA 接收與回覆判斷的 C/C++ 契約

從原 APK 的兩個 JS 模組重建接收 parser、`Verify` 及 W 回覆接受式。
這是 host 上的可讀 C11/C++17 語義程式，供核對原 BOOT／Runtime 回應。
它沒有藍牙傳送器、UID、Flash 存取、MCU 模擬或可刷映像，不會呼叫伺服器。

`source-map.json` 是六個已封存的原碼片段。`verify-source.py` 每次從本地
原 APK 的 ZIP／wxapkg 成員重新核對整體 SHA256、索引、JS SHA256、六段
原字元範圍及逐 byte 內容；不執行 JS。APK 必須符合
`10d7d92f16d7806d841fcfd152b318601f6c234a2445e99e0729709aacc9c3ee`。

## 已重建的行為

- 以 `55 7F`、command、BE16 長度及 sum8 接收，跨 notification 保存狀態。
  payload 上限 4096；notification 間隔至少 500ms 時只重設 state。
- 初始 buffer 是 `[0]`；長度零的 frame 保留既有 buffer。checksum 正確後
  先呼叫 callback，正常返回才把 buffer 重設成 `[0]` 並清 state。
  checksum 失敗、timeout 或格式失敗不清 buffer。因此空 wire ACK 可能是
  callback 的一 byte `[0]`，也可能帶著先前未成功接收的 buffer。
- callback 拋例外／效果未知時停在當前前綴，不假設後續清理已完成。
- `Verify` 只比較收到的非空前綴，沒有完整頁長度檢查。缺少目前 page
  且收到非空資料時保留 UNKNOWN；原 JS 此時可能拋例外。
- W 另有一 byte 零捷徑，或要求回覆長度等於 metadata 的 PageSize 後才
  `Verify`。PageSize 是呼叫者輸入，沒有從韌體或 APK 推定固定常數。

乾淨 parser 的空 wire R 回覆可變成 `[0]`，符合 page <256 的第一個
page-index 高 byte；這只證明原接受式能通過，**不證明任何 Flash 頁面已
讀回或驗證**。W 的兩 byte page-index 回覆在 PageSize1026 時不能通過。

## 限制與使用

本介面只覆蓋已初始化 parser、有效 byte-array、可精確表達的日期差值，
以及同步且不重入／不改 parser 欄位的 callback。輸入不與 parser storage
重疊；callback 只在呼叫期間借用 buffer，返回後不得保留／使用該指標。
原 JS 是換一個新 array，這個固定 storage 的介面不重建 array identity／
lifetime。原 TypedArray 配置假設成功。它保留 callback 當場修改 buffer
的能力，但不重建 JS 物件別名、allocation exception 或外層 SDK
exception handling。C 的 UNKNOWN 是證據邊界，不能解讀成原 JS 回傳碼。
`ak_w_accepts` 只重建接受式；`Read`／`Write` 的 index、retry、timer、
updataIng、UI、server updateok 等外層控制不在本介面內。

```powershell
.\verify.ps1 -Apk '<原 APK 絕對路徑>'
.\verify.ps1 -Cpp -Apk '<原 APK 絕對路徑>'
```

在原工作區可省略 `-Apk`，自動選本地 publish-tsl9 的同一 APK。
不尋找其他下載來源；缺檔會明確失敗。每次先核原 APK 來源，再以 MSVC
`/W4 /WX` 編譯、執行合成 host tests，保存 compiler/source/EXE 雜湊。
測試覆蓋完整 W echo 的每一個分段點、clean/stale 空 ACK、500ms 邊界、
checksum wrap、4096 長度、缺 page、前綴判斷及 callback 例外前綴。

最初 TDD baseline 的第一項前綴測試確實失敗（exit1）；其獨立 build
收據保留。後續綠色 host 結果只證明這個 C/C++ 契約在合成資料上的行為，
不證明原 APK 執行、原硬體或 OTA。`native_BIN=false`、`OTA_ready=false`。
