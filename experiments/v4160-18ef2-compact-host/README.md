# 18ef2 compact host fixture

獨立副本：`candidate.c` 是既有候選的副本，`harness.c` 複用既有 callback/event-budget 結構；不依賴相鄰 untracked 程式。`fixtures.h` 用 C macro 固定四條有序 bus script：normal、32-bit source wrap、覆疊 alias、busy polling。每個 callback 比對事件種類與地址，write 額外比對值，返回時比對結果及事件數。alias 的後續讀值固定為首個字；這是腳本假設，不是一般記憶體模擬。

poll 的三次 control 讀值分別為 `13579bdf`、`2448ace0`、`a5b3c4d6`，對應寫值 `13579bdf`、`2468ace0`、`a5b2c4d6`；包含初始、複製中及最後忙碌讀取。腳本不證明目標 ABI、硬體或 nonreturn 行為。事件預算無法終止不呼叫 callback 的無窮迴圈，未來實測須另加外部 timeout。

在使用者授權下，使用本機 MSVC `cl.exe` file version `19.44.35228.0`（SHA-256 `88c8344236a27a6e727e0a8edc49aaa2690bdc7a9464b9d18cc7abe70a9f1c0d`）和 `link.exe` file version `14.44.35228.0`（SHA-256 `ca11e6c45debd34bf652dfe984c5360a531a005ed78bf72852330c9c2590cf0d`）在新建暫存目錄編譯／連結此 harness，設定 `/std:c11 /W4 /WX`，分別不加與加入 `/DNDEBUG`。兩次編譯均退出 0；以 15 秒外部 timeout 執行各 host executable，均輸出 `normal: pass`、`wrap: pass`、`alias: pass`、`poll: pass` 並退出 0。編譯依賴 VS Build Tools `14.44.35207` 與 Windows SDK `10.0.26100.0` 標頭和 libraries，未逐一固定其 hash，工具本身先核對 SHA-256。

另在新的隔離暫存目錄複製三個 C 檔，將 candidate 第一次 control 寫入的 OR mask 由 `0x10000` 改為 `0x20000`；mutant 成功編譯，但執行於 `normal` 事件 1 偵測寫值不符並以 1 退出。這是一個負例，不證明測試可偵測所有錯誤。沒有執行 target、模擬、網路或硬體，測試僅驗證上述有限 host callback 腳本，不能推論原始半字／word bus 寬度、ABI、原址 codegen、完整影像或真實裝置效果。

```sh
python experiments/v4160-18ef2-compact-host/test_fixtures.py
python -O experiments/v4160-18ef2-compact-host/test_fixtures.py
```

Python 獨立展開有限 macro 語法，逐一比較原始 `../v4160-18ef2-c-harness/fixtures.h` 的四筆登記與 812 個事件（201/201/201/209）。原始檔存在但不符即失敗；不存在時仍檢查固定完整 trace SHA-256 和各自事件數，不依賴原始檔。SHA-256 輸入為每案例一行 `name arg source result`，後接各事件 `kind address value`，數值均為八位小寫十六進位，以空格分隔，每行含 LF。fixture header 另有位元組 pin，保護 Python 未展開的登記 macro 等部分；更新 pin 前須人工審核。Python 驗證不是 C 編譯器或 C 執行的替代品。
