# Public evidence redaction

[繁體中文](README.md) · [简体中文](readme.zh-CN.md)

Personal paths and account names in the current public text tree use variables. Byte-exact original receipts remain in a private local ZIP outside Git. Public copies are derivatives, not original verification receipts.

- [manifest.json](manifest.json) lists original/public SHA-256 values for 816 derivatives and the private backup digest.
- Dependent text hash references were rebased; changed text uses LF. BIN/APK bytes and their hashes were preserved.
- Test statuses in old receipts remain historical. Redaction does not rerun tests; old argv containing variables is not directly replayable.
- Git history was not rewritten: earlier commits may retain old paths. Git configuration, remotes and identity were preserved.

From the project root:

```sh
python -B scripts/anonymize_public_evidence.py --check
python -B tests/test_public_evidence_redaction.py
```

Keep the original ZIP local. Set `TSL9_ORIGINAL_ZIP` to its location and run `python -B scripts/anonymize_public_evidence.py --verify-private "$TSL9_ORIGINAL_ZIP"` to verify it. Never commit the original ZIP or private edit plans.

If a sandbox restricts the default temporary directory, set `TSL9_TEST_TMP` to a writable test directory. [This verification](verification.json) covers only the listed offline checks.
