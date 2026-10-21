# IRQ 暫存器限制：原生編譯受阻

凍結的可讀 C 實作明確保留原本 A2/A3 邊界，並提交精確 A0/A1/A4/A5 輸出。主要原生組態是 RV32IMAC_Zicsr、ILP32、**-Oz**，僅配置 A0/A4/A5；A1 只供固定暫存器提交使用，其餘整數暫存器連同 SP 全部保留。本機 Android NDK Clang 18.0.2 對 C11、C++17 的五個函式均回報：

```text
Stack pointer required, but has been reserved.
```

沒有產生 object 或連結 ELF，因此目前不能宣稱新的原生函式大小、編碼暫存器保留、機器輸出樣式、剩餘空間或原位置適用。舊版另一組暫存器契約的 IRQ/helper 118/22 bytes，不能直接當成這份候選的配置預算。

本輪只依授權補測三個有限診斷組態，與原始組態組成 2×2 矩陣；都使用 -Oz，且不放寬 A2/A3/SP/GP 限制。

| 原始碼 | 可配置暫存器 | C11 | C++17 |
|---|---|---|---|
| 凍結原版 | A0/A4/A5 | 五個配置錯誤 | 五個配置錯誤 |
| A0 `+r` 提交改為回傳值，直接回傳該值 | A0/A4/A5 | 五個配置錯誤 | 五個配置錯誤 |
| 凍結原版 | A0/A1/A4/A5 | 五個配置錯誤 | 五個配置錯誤 |
| 相同的回傳值診斷版 | A0/A1/A4/A5 | 五個配置錯誤 | 五個配置錯誤 |

診斷來源僅寫在本機 build 內，沒有修改正式 C/header。沒有嘗試或採用分支優先改寫、SP wrapper、允許 A2/A3 配置或其他最佳化模式。回傳值版本確實移除一段獨立 return SSA 生命期，但單獨修改與搭配 A1 配置都沒有解決問題。精確的配置根因尚未確認，已保留真實 compiler 診斷。

下一個具體實作問題是 helper 的生命期布局：實際最佳化 IR 會先計算 OR 與 AND_NOT、select 並 store，**之後**才分支至兩組暫存器提交。可讀 C 若改成各分支內才計算、store、提交，可能改變生命期重疊。本輪沒有測試，這是下一步實作項目，尚非已證明的修正，也不能據此放寬暫存器契約。

同一凍結組態仍可輸出最佳化 LLVM IR。獨立 IR 檢查確認 **20 項有順序的 CSR/MMIO 效應**、六組新的 32-bit RCC 讀改寫、**七次完整暫存器精確提交**，以及最後一次讀改寫的回傳值。各 helper 以完整 32-bit enabled 值判斷零／非零，保留精確非零 A1，並提交依分支選擇的實體 base 與讀取前值。原版 C/C++ 各有六個 IR 文字負向控制，會拒絕缺少／錯誤提交、CSR mask、PFIC 寬度、RMW mask 和錯誤回傳值。這些是 IR／原始碼證據，並非原生機器碼證明。回傳值診斷版的 IR 已保留及雜湊，但沒有冒用原版 input-only checker 通過的名義。

`results.json` 選定八份逐 byte 相同的結果副本；`final-audit.json` 封存 checker、CLI、metadata 與分開的語言文件。失敗 compile log、IR、診斷來源保留在本機 `build/`；重新產生不依賴舊 build。跨平台命令請見 [English](readme.en.md) 的 code block。

主要 CLI 同時回報 `expected_native_blocker_reproduced: true` 與 **`native_verification_passed: false`**；process exit 成功只表示重現預期阻礙與獨立 IR 證據，不能視為韌體編譯成功。若另一本機編譯器產生不同結果，CLI 會拒絕默默當成原生驗證完成。可用 `--clang` 指定本機執行檔。唯讀 checker 可加 `--require-local-builds` 要求選定歷史輸出必須存在；只核對 metadata 不等於重新編譯。

回傳值診斷 CLI 為 `probe_commit_return.py`，加 `--allow-a1` 選擇最後的組合診斷；`probe_allocator_a1.py` 重現原始碼只開放 A1 配置的診斷。兩者都接受 `--project-root`／`--tool-dir`，僅使用本機工具並如實記錄失敗。沒有執行目標、ISA 模擬、網路、裝置 I/O、原映像修改、韌體 BIN 或 OTA 操作。後續必須先解決配置問題，且以實際機器碼證明原暫存器與正常輸出契約，才能進入配置整合。
