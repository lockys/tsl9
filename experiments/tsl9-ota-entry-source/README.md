# 0x14056 入口的來源整合

[English](readme.en.md)

來源 `src/native/receive/ota_entry_14056.inc` 描述 `0x14056..0x1408E` 的 56 bytes：建立 stack frame、保存暫存器，以及原始命令分派的初始分支。它必須置於原位址並接續既有程式，不能作為獨立 C 函式呼叫。

C／C++ 產物各有五個 RISC-V branch relocation；建置器核對類型、位置、目標，再於 `0x14056` 連結並與原始 bytes 逐 byte 比較，才把編譯結果放入候選映像。入口與先前結尾共 70 bytes 由來源編譯，其餘 3,058 bytes 仍為原始載體；JSON 中的完整原始 bytes 保留作對照。

`python scripts/verify-full-source-isolation.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 檢查不含既有 BIN 的 190 檔來源副本可重建兩種候選映像；`scripts/verify-payload-active-gates.py` 重驗條件式連結及先前控制流程。位元組相同不代表完整功能、ROM／ABI 或實機安全性已確認。
