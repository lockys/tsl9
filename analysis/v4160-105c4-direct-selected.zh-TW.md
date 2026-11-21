# v4.1.60：按既有配置直接連結選定區段

延續 [六段依賴驗證](v4160-105c4-direct-dependencies.zh-TW.md)，以既有 compact layout 決定原址，將保存的 140 個基準輸入或 141 個 split/leaf 候選直接交給 LLD；其中候選 leaf 重建了輸入 addrsig 身分。配置計畫取自聚合基準，但最終連結不以聚合物件為輸入。僅在暫存目錄產生診斷 ELF。

一般 Python 與 `-O` 各通過 C／C++ 基準及候選四路。每路 6,278 個配置區段、73,672 bytes，逐段對照原 BIN 得 0 差異；同語言基準和候選的區段型別、旗標與內容也一致。GP 採數值設定；尚未加入 72 個既有別名時有 78 個未定義符號，加入後剩 6 個，再用六個既知數值見證才能完成連結。全部診斷輸出均零 PT_LOAD。

此結果使用保存的既有 6,278 區段基準，不能解讀為修好了另一套 6,266 區段來源基準的 93 個 TX 差異。既有來源／不透明資料也未被此測試重新反組譯。未選 3,128 bytes 和實際外部提供者不在本輪驗收內；聚合 addrsig 的 sh_link=0 仍未解決，這不是正式建置或可刷映像。下一步按缺口優先處理 3,124 bytes dispatcher 與 4 bytes 資料，使兩者以實體區段加入直接連結，再盤點剩餘的數值見證。

原 BIN 與正式來源未改；本次只發布報告。重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe>`。
