# 獨立 `.comment` 投影守衛

`guard.py` 只使用 Python 標準庫。它從本機 `experiments/v4160-b0b0-partial-relink/verify.py` 的 `comment_projections` 和 `need` 抽出；本機 partial verifier 以 SHA-256 pin 讀取並直接執行同一份 guard bytes。抽出後的本機離線 replay 中，C11 和 C++17 兩組 partial-link 選定 facts 與各自獨立 leaf 原址 10 bytes 檢查均通過；partial verifier 及其 unit-split 依賴尚未提交，暫存 ELF 已清除，不能由本目錄單獨重播該結果。這不是 combined unit 最終連結、ABI 或完整 BIN 驗收。

## 介面及假設

`comment_projections(baseline, combined, leaf_partial, views)` 接受三份已解析物件及對應三份 view，回傳三份 `SimpleNamespace` view；失敗時拋 `ValueError`（缺少欄位等不符合介面者亦可能拋其他例外）。物件需提供 `sections`、`symbols`、`relocations` 和 `data(section)`；view 另需提供 `kind`、`flags`、`function_bytes`。section 和 symbol 為 mapping；relocation 的 `symbol` 必須指向原 symbol 物件。呼叫者需提供順序一致、恰好三份的 view，且 view 內保留的 symbol 使用原物件 identity；守衛不解析或驗證 ELF，也不檢查 view 本身的來源或完整性。

三方 `.comment` 各須唯一、非空、有效 section index、SHT_PROGBITS；type、flags、size、alignment、address、link、info、entry_size 和完整 section bytes 相同，bytes 長度必須符合 size。不比較 section index、檔案 offset 或 name offset。每邊恰有一個空名、零 value/size/other、info=3 的 SECTION symbol；所有其他指向 `.comment` 的 symbol 須是 ASCII `$d.[0-9]+`、value/size/info/other 為零，均不可被 relocation 以 identity 引用。其他 alias 和 global 一律拒絕。leaf_partial 須恰有一個 mapping，combined 數量須等於 baseline 加 leaf_partial，只忽略數字後綴。輸出只從既有 views 移除這些 mapping，保留 SECTION symbol 和其他內容；原物件不修改。

這是嚴格的局部實驗假設，不是 linker 通則，也不證明 symbol 來源、未檢查的欄位或整體等價。呼叫者仍需比較其他保留 facts，並自行保證 parser 的正確性與輸入可信度。此守衛不依賴 compiler、linker、target 或網路。

## 合成測試

在 repo 根目錄執行（也可將本目錄獨立複製後，在其目錄執行 `python -I -S -B test_guard.py`）：

```text
python -I -S -B experiments/v4160-b0b0-comment-guard/test_guard.py
python -I -S -B -O experiments/v4160-b0b0-comment-guard/test_guard.py
```

只使用標準庫及 synthetic objects；包括 PROGBITS/NOBITS、mapping 數量及 paired extra、metadata/bytes、alias、relocation、缺少或重複 SECTION symbol。`-O` 同樣保留所有檢查。測試不讀 ELF、不呼叫 compiler/linker、target、模擬器或網路，也不是實際 replay。
