# 本機路徑

[English](local-paths.en.md)

專案位置由腳本自身位置取得，不依賴使用者帳號或目前工作目錄。需要外部工具的舊腳本使用以下環境變數；新 verifier 也可直接傳入 `--tool-dir` 等既有參數。

| 變數 | 用途 |
| --- | --- |
| `TSL9_LLVM_BIN` | 含 clang、ld.lld、llvm-objdump 的既有工具目錄 |
| `ANDROID_NDK_HOME`／`ANDROID_NDK_ROOT` | 未指定 LLVM 目錄時，尋找 NDK 內唯一可用 prebuilt/bin |
| `TSL9_R2` | 既有 radare2 執行檔；未設定時使用 PATH |
| `TSL9_ANALYSIS_WORKSPACE` | 只有需要原始封存工作區的歷史複核才需設定 |
| `TSL9_PYTHON` | 舊 PowerShell 入口使用的 Python；未設定時由 PATH 尋找 |

環境變數內容只存放在自己的 Shell／本機設定，不提交到 Git。路徑可含空白。找不到工具、指定錯誤或有多個候選時會停止並指出缺少的設定，不下載或猜測其他帳號目錄。

可執行 `python3 scripts/project_paths.py --select project-root` 檢查解析結果。這只讀取本機路徑，不執行韌體或連接硬體。

路徑改動會改變腳本的來源雜湊。舊收據保留為當時的證據，不能拿來宣稱修改後腳本已通過；需要重新驗證的流程須產生新收據。
