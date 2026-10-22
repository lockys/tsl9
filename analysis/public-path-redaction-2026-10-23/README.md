# 公開證據匿名化

[English](readme.en.md) · [简体中文](readme.zh-CN.md)

目前公開文字檔中的個人路徑、帳號名稱已改為變數。原始收據逐位元組保存在 Git 之外的本機私有 ZIP；公開副本是衍生資料，不能冒充原始驗證收據。

- [manifest.json](manifest.json) 記錄 816 份副本的原始／公開 SHA-256，以及私有備份雜湊。
- 相依的文字檔雜湊引用同步更新；換行統一為 LF。BIN／APK 位元組與其雜湊未修改。
- 舊收據的測試狀態只是歷史記錄；匿名化不代表重新執行測試。含變數的舊 argv 不能直接當作重播指令。
- 未改寫 Git 歷史：舊提交仍可能包含先前的路徑。Git 設定、遠端與身分設定維持原樣。

從專案根目錄檢查公開副本：

```sh
python -B scripts/anonymize_public_evidence.py --check
python -B tests/test_public_evidence_redaction.py
```

原始 ZIP 留在本機。將其位置放入 `TSL9_ORIGINAL_ZIP` 後，使用 `python -B scripts/anonymize_public_evidence.py --verify-private "$TSL9_ORIGINAL_ZIP"` 復核；不要把原始 ZIP 或私有編輯計畫提交到 Git。

若沙箱限制預設暫存目錄，可將 `TSL9_TEST_TMP` 設為可寫目錄供測試使用。[本次驗證](verification.json) 僅代表列出的離線檢查。
