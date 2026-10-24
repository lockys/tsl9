# 原排程器：離線里程碑

[English](readme.en.md)

新增 [C/C++ 實作](../../src/native/receive/scheduler.c)，覆蓋完整9124–9250／300B／115指令。兩語言的實際編譯碼在純資料原位址重定位後與官方BIN相同。真實部分連結共5702B code＋60B table／460 FUNC／423 RELA，補上9124定義，仍有74個未解析符號及額外常駐／間接依賴。不能當作可燒錄BIN。

[摘要與缺口](summary.json) · [配方及架構限制](../../experiments/tsl9-scheduler/README.md) · [收據來源](publication-provenance.json) · [候選ROM關聯](resident-reference-association.json)

100組來源比較／200物件及正常產物重播通過；原98組及589個artifact記錄不變。保留15槽、fresh狀態、乘法低32bit、unsigned除625與低5bit位移語義。沒有新畸形輸入／負例矩陣，也沒有重試先前被安全檢查中止的覆核。

歷史WCH header將四個槽關聯到事件設定、工作啟動、週期工作與訊息釋放宣告。保留的V1.31／V1.40映像具有不同指標值。這些屬參考級關聯；沒有把候選地址或實作綁入重建，也沒有證明實機ROM。

五份公開收據中四份保留原位元組，一份只替換本機路徑並明示衍生副本，附原始／公開SHA-256及完整JSON可逆核對。675個原件的驗證封存（包含參考庫資料）僅留本機。匿名副本不是原始重播輸入。

```sh
python3 scripts/check-scheduler-publication.py
python3 scripts/check-scheduler-resident-references.py
```

兩命令只讀，需保留的本機原件及參考資料。無網路、硬體或目標執行；可刷寫韌體與硬體相容性仍未完成。
