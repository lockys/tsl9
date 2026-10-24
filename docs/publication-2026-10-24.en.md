# C/C++ reconstruction publication scope

[繁體中文](publication-2026-10-24.zh-TW.md)

This publication includes the selected [C/C++ sources](../src/readme.en.md), supporting experiment sources, and static analysis reports dated 2026-10-24. It preserves the latest upstream Morphe changes that resolve tool paths through configuration and environment variables. `TSL9_LLVM_BIN` can select the local compiler tools.

There are 116 C/H files. The selected component matches 22,580 original bytes at their nominal addresses and retains 70 unresolved dependencies. Its diagnostic ELF has no PT_LOAD. Complete reverse engineering, hardware startup, and functional OTA operation of reconstructed firmware remain unproved. See the [latest settings/persistence evidence](../analysis/settings-defaults-2026-10-24/readme.en.md).

New publication files are checked for personal paths and credential candidates, and new commits use a GitHub noreply identity. Original local build receipts, private delivery data, backups, unreviewed older work, and new binary files are excluded. Original receipts remain local; their hashes are not fabricated or rewritten. References to local `build/` receipts are not bundled public artifacts and do not establish that another party has reproduced the results.

This does not rewrite published Git history or modify/re-upload the existing APK. Historical personal paths/email and unresolved SDK constants in that APK remain; a clean incremental scan is not a claim that the entire repository/history contains no sensitive information. No candidate credential is tested, target firmware executed, or hardware operated.
