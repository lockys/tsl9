# 公开证据匿名化

[繁體中文](README.md) · [English](readme.en.md)

当前公开文本中的个人路径、账号名称已替换为变量。原始收据逐字节保存在 Git 之外的本机私有 ZIP；公开副本是衍生资料，不能冒充原始验证收据。

- [manifest.json](manifest.json) 记录 816 份副本的原始／公开 SHA-256，以及私有备份摘要。
- 相关文本摘要引用同步更新，换行统一为 LF。BIN／APK 字节及其摘要未修改。
- 旧收据的测试状态仅是历史记录；匿名化不代表重新执行测试。含变量的旧 argv 不能直接重放。
- 未改写 Git 历史：旧提交仍可能含先前的路径。Git 配置、远程仓库与身份设置保持原样。

从项目根目录检查：

```sh
python -B scripts/anonymize_public_evidence.py --check
python -B tests/test_public_evidence_redaction.py
```

原始 ZIP 留在本机。将其位置放入 `TSL9_ORIGINAL_ZIP` 后，使用 `python -B scripts/anonymize_public_evidence.py --verify-private "$TSL9_ORIGINAL_ZIP"` 复核；不要将原始 ZIP 或私有编辑计划提交到 Git。

若沙箱限制默认临时目录，可将 `TSL9_TEST_TMP` 设为可写测试目录。[本次验证](verification.json) 仅涵盖列出的离线检查。
