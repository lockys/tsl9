# 十一個函式的數值 interior 引用檢查

[English](readme.en.md)

這項離線補充檢查針對原始官方映像、前輪 IRQ 映像與新十一函式候選映像，逐 byte 位置搜尋十一個原始函式範圍內、排除入口的 32-bit little-endian 數值。函式範圍來自已封存的 entry-order 整合規劃；三個輸入均核對完整 SHA-256 及 76,800-byte 尺寸。

每份映像檢查 1,030 個數值與 76,797 個可容納四-byte 數值的位置，包含未對齊位置。數值形式分別使用原始 VMA 及加上 `0x08000000`；檢查這兩種數值不證明它們是原機實際映射。十個合成控制確認兩種數值形式、四種對齊位置可被找出，並排除真正函式入口。

實際結果與限制見 `report.json`。這只補充已記錄 relocation 與直接分支清單。沒有找到 literal 不等於沒有計算而來、拆開編碼、加密、ROM 或執行期引用，亦不證明遺失的 program `+8` 指令邊界可以安全忽略。此工具不執行或模擬原始／重建韌體，不建立 BIN，不證明硬體或 OTA 相容性。

執行方式：`python scan.py --project-root <專案目錄> --original <官方BIN> --previous <前輪IRQ候選BIN> --candidate <十一函式候選BIN> --check`。亦可使用 `sh scan.sh` 傳入相同參數。原生 Windows Python 執行結果與 shell／Linux／macOS 執行證據分開，不能互相取代。
