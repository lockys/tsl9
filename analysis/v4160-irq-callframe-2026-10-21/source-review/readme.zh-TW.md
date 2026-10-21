# 呼叫框架的獨立主機審查

本範圍將凍結的 `interrupt_callframe.c` 與 `rcc_helpers.c` 作為兩個實際編譯、連結的主機編譯單元審查。直接重用 `tsl9-v4160-placement-2026-10-21/code-review` 已封存的獨立測試，不複製判定邏輯，也不修改舊封存。輸入與正式回條雜湊見 [review.json](review.json)。

C11 與 C++17 各驗證四組、3,820 個案例、138,312 項斷言。獨立 helper 矩陣涵蓋四個位移、完整 32 位元遮罩與資料，以及八種 enabled 值，包含不等於 1 的非零值。啟用分支觀察到的 A4 為基底、A5 為當次讀值；停用分支 A4 為當次讀值、A5 為基底。因此可以辨別基底與完整存取位址混用。

主初始化函式逐項檢查 20 個外部效果的順序：清除 CSR、六組獨立讀寫、六次 PFIC 寫入、設定 CSR。六次讀值刻意不同，同時檢查寫入寬度、位址、資料、helper 順序、正常輸出觀察值與實際 C 回傳值。合成 CSR 在效果之間改變，避免誤用舊快照仍通過測試。位址僅作為測試鍵值，沒有轉成主機周邊指標。

每種語言各有 30 個實際編譯且執行後被斷言拒絕的變異版本，涵蓋呼叫目標與順序、enabled、最後回傳、CSR、PFIC 寬度與位址、動態遮罩、分支輸出、快取讀值與先寫後讀。編譯失敗不計為成功攔截行為變異。

這些結果證明主機函式連結與合成環境下的可觀察行為。主機 `CF_CALL` 是一般 C 呼叫，原生分支則使用內嵌組語 JAL 與 clobber 宣告。主機 `CF_RETURN` 回報明確傳入的輸出 tuple，沒有擷取目標機真正的 A1/A4/A5。CSR、記憶體與固定暫存器操作也由主機介面替代，因此本審查不證明目標堆疊框架、儲存順序、暫存器保留、JAL 可達性、指令一致性、配置或硬體行為；原生驗證必須另外綁定實際連結產物。全程沒有執行目標程式、ISA 模擬、裝置操作或網路請求，也不代表可 OTA 燒錄。

在有 C/C++ 編譯器的 checkout 可重跑主機測試：

```sh
sh verify.sh --project-root /absolute/project --language c
sh verify.sh --project-root /absolute/project --language cpp
python3 check-review.py --project-root /absolute/project
```

`--project-root` 指向包含 `experiments` 與 `scripts/portable_verify.py` 的 checkout。旁側證據目錄支援既有 `tsl9-` 與發佈用縮短名稱。此處於 Windows 直接執行 Python；沒有執行 shell wrapper。重跑會新增唯一且排除發佈的 `build/` 目錄與 `receipts/` JSON 副本。封存回條記錄執行檔、輸入與編譯器雜湊；歷史 EXE、物件檔、編譯日誌與變異原始碼僅留工作目錄排除的 `build/`，不納入發佈證據。重跑只執行自行編譯的主機測試程式。
