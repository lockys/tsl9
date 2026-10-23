# 功能分派器：離線驗證紀錄

[English](readme.en.md)

三個 [C/C++ 單元](../../src/README.md) 重建 14D2E–154A6、829E getter 與兩張相對跳表。1922B 程式及60B表在原位址的資料重定位驗算後與官方 BIN 相同；接入既有元件共5088B程式、60B表，仍有70個直接未解析符號與額外間接依賴。不能作為可燒錄韌體。

[摘要](summary.json)、[回呼依賴](callback-frontier.json)、[有限覆核狀態](independent-review.json) 與 [完整配方及限制](../../experiments/tsl9-feature-dispatch/README.md) 分別記錄已確認結果與缺口。最新正常 C11/C++17 產物通過；新增拒絕檢查未執行新的負例矩陣，後續獨立覆核已因安全檢查停止，沒有改道重試。

公開10份收據中7份保留原位元組，3份只替換路徑並標示衍生副本。[來源清單](publication-provenance.json) 保留原始與公開 SHA-256、大小及路徑替換可逆的 JSON 全值核對結果。原始收據及781個檔案的封存只保留本機；匿名副本不冒充原始重播輸入。

```sh
python3 scripts/check-feature-dispatch-publication.py
```

此命令唯讀核對公開副本與本機原件；需要原始收據。本次無網路、硬體操作或目標程式執行。
