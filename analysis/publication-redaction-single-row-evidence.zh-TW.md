# Publication 身分差異：單筆歷史 redaction 證據

此紀錄只核對 `analysis/v4160-adc-caller-2026-10-22/abi-review/actual-c.json` 一筆，不修改或重新封存 publication manifest。歷史匿名化 commit `f23f6bd2b943da416e3e595cefe407fe52554505` 的父節點為 `e3406c69dc76db553eec685f4b9fa2fafa344646`。以下為本機 Git 物件的內容核對，使用 `GIT_NO_LAZY_FETCH=1` 與 `git --no-lazy-fetch`，不從 promisor 遠端補取物件。

| 證據 | bytes | SHA-256 |
|---|---:|---|
| 父節點的 publication manifest row | 30389 | `c0f156e81338337267c642c8d251f493d5d392ef28671631347f29267591b508` |
| 匿名化提交的 publication manifest row | 30389 | `68dbc8865098b03e4f1789805fe8122f0c22a020c9342ff59b24349bcb4715e5` |
| 父節點該路徑的實際 Git blob | 30389 | `c0f156e81338337267c642c8d251f493d5d392ef28671631347f29267591b508` |
| 匿名化提交該路徑的實際 Git blob | 29967 | `68dbc8865098b03e4f1789805fe8122f0c22a020c9342ff59b24349bcb4715e5` |

兩個 blob 的 Git object ID 分別為 `ace375f2f965fefbf5b6ff8f30a7fae06f59fd8c` 與 `691ff77c4f77f333bbbc7dceacca0c16c3ad0625`。匿名化提交的 `analysis/public-path-redaction-2026-10-23/manifest.json` blob 為 `83f407daf0fdda34634817db40931b4590402e4a`；其中該路徑的 `original_sha256`／`original_bytes` 和 `public_sha256`／`public_bytes` 分別與上列兩個 blob 一致。該項也標記 `personal_path_or_label_changed`、`dependent_text_hash_pins_changed` 和 `native_editor_LF_representation` 為 true，並將結果描述為 anonymized historical/public derivative，而非原始 receipt。

因此，這筆 publication row 在該次提交後保留舊長度，卻改用公開副本的新 SHA-256；實際公開副本短 422 bytes。這支持**此單筆**長度差異與當次匿名化變更的關聯，不證明逐 byte 轉換規則、私有原件真實性或其他差異的成因。未稽核全部 354 筆，也不處理另有 digest 差異的項目；不能據此重算整份 manifest 或宣稱 publication 驗證通過。
