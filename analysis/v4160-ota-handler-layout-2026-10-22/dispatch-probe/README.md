# Command switch 單一負結果

[English](readme.en.md)

只將 compact568 的最外層五個完整32-bit command if 判斷改為 switch/cases，保留未知command no-op、各分支effects／locals、共用末端reply labels、完整八暫存器bridge及原flags。來源以apply_patch複製到本scope/build/source/src，未改舊model或seal。

實際 C11/C++17 各為568B／193指令／frame48／9真UND／20RELA。payload SHA `b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af`，與已封存baseline逐byte同hash，**沒有改善，不建立新model**。未重編baseline、未重跑不變HOST suites，沒有進一步variants／flagsweep。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/dispatch-probe/check.py --project-root .
python3 -B apk-analysis/tsl9-v4160-ota-handler-layout-2026-10-22/dispatch-probe/check.py --project-root . --receipt PATH/verification.json
```

發布版case可位於analysis/v4160-ota-handler-layout-2026-10-22；checker依自身位置尋找metadata。預設只核對seal／baseline來源pins／兩份選定receipt metadata，不讀build、不宣稱native archives replay。明示--receipt才重讀同project root下保留的真實source＋object／IR／MD／logs；缺檔時拒絕。歷史W build位置不是發布預設依賴，build/source與archives不發布，也不宣稱在沒有archives的發布目錄完成actualreplay。

`probe.py` 是這次四exact native recipes的診斷driver：resource query、-MD object、IR、完整M/A/C/Zicsr objdump；產物create-only，source/tool/resource before-after pins和全部artifacts可read-only replay。保留它以重驗現有本機archive，不把negative probe升格為新promoted producer。source-change.patch記錄純C dispatch差異。

原始530B範圍仍超出38B，完整ABI／placement仍false。沒有link、numericproviders、BIN、RV32執行／模擬／硬體或網路操作。
