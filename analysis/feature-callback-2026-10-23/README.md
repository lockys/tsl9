# 回呼與校驗：離線里程碑

[English](readme.en.md)

新增 [C/C++ 實作](../../src/native/receive/feature_callback.c)：七段314B／109指令，在原位址做純資料重定位後與官方BIN逐位元組相同。整合後共5402B code＋60B table，原圖三個直接依賴已有真實定義；仍有75個未解析符號及額外間接／常駐依賴。ET_REL的VMA為0，不能當作可燒錄BIN。

[摘要與缺口](summary.json) · [配方、失敗試驗與架構限制](../../experiments/tsl9-feature-callback/README.md) · [收據來源](publication-provenance.json)

98組來源比較／196個物件與兩語言正常產物重播通過。原96組及577個artifact記錄不變。沒有重試被安全檢查中止的覆核，也沒有新增畸形輸入／負例矩陣。

公開7份收據中6份保留原位元組；1份只替換個人路徑，明確標示衍生副本，附原始與公開SHA-256及可逆JSON核對。675個原始檔的驗證封存僅留本機，匿名副本不當作原始重播收據。

```sh
python3 scripts/check-feature-callback-publication.py
```

需要保留的本機原件。尚未產生可刷寫韌體或證明實體硬體相容性。可考慮後續增加被動校驗錯誤及回呼／待排程工作診斷；目前只是提案。
