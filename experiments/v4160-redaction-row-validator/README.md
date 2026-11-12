# 單筆 redaction row validator

純 Python library，無 CLI、檔案存取、Git、網路或目標執行。`validate(old_manifest, new_manifest, redaction, old_blob, new_blob, parent_id, commit_id)` 只接受呼叫者提供的 bytes 與字串；成功回傳 `True`，失敗拋出 `Invalid`。正式政策使用 `PIN`，`validate` 不提供 spec 參數，僅防止意外的參數覆蓋；同一 process 可以 monkeypatch 模組、常數或函式，不應信任遭竄改的 process。`validate_with_spec` 是同一驗證器的可注入規格運算層，供記憶體中的 synthetic 測試，不代表正式政策。不要把使用自訂 spec 的結果當成正式驗證。

Publication JSON 根物件的 `files` 必須是 row 陣列，各 row 均需字串 `path`、非負整數 `bytes` 和小寫 64 字元 SHA-256，路徑不得重複。兩份都完整解析，不用行掃描或 substring。JSON 所有層級均拒絕重複鍵、非有限數字及不完整 UTF-8；blob 也必須完整 UTF-8。redaction 檢查 schema、HEAD、歷史標記、指定 row 的 digest、長度、flags 和 status，並固定其 Git blob oid。以 SHA-1 計算 `blob <byte length>\0<bytes>`；blob 同時檢查 SHA-256、長度及 oid。新 publication row 的長度刻意要求仍是舊長度，而非新 blob 長度。

限制：每份 publication 最多 32 MiB，redaction 最多 8 MiB，每份 blob 最多 2 MiB，各 files 最多 200,000 項；超限拒絕。JSON 解析深度超過 Python 限制時拒絕。輸入已由呼叫者載入記憶體，這些限制不限制呼叫者事先分配的記憶體。錯誤不回傳內容，避免洩漏資料。

只驗證指定內容與呼叫者提供的 ID 是否符合固定數值；不驗證 Git commit membership、父子關係、私有原件真實性或轉換規則，沒有讀 Git，也不能據此聲稱核對完整歷史或全部 354 項。兩份 publication manifest 本身未被 pin，只檢查其結構與指定 row，不聲稱其他 row 的內容正確。

自動測試全為 synthetic，從本目錄執行 `python -m unittest -v` 及 `python -O -m unittest -v`；測試不讀取真實 manifest 或 Git objects。另曾以 `git --no-lazy-fetch cat-file blob` 從本機讀取兩份歷史 manifest、redaction manifest 與兩個 blob，將 bytes 傳給固定政策 `validate`，得到 `True`；ID 為呼叫者提供，這次 library 呼叫本身不驗證親子關係或 tree membership。缺少本機物件時不得改用自動抓取補足。
