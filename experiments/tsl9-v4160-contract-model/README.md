# V4.1.60 可讀 C/C++ Flash 呼叫契約

本模型將 ID2966 原始 `197BE` wrapper 及其五個直接相依本體翻成可讀 C11 / C++17 控制流程；不是實體 Flash 驅動、完整原機 ROM、原作者原始碼或 OTA 映像。`source-map.json` 固定 76,800-byte 原始韌體及六個來源範圍，共 294 bytes。原指令仍由獨立的 `tsl9-v4160-startup` 工程保存；此工程不改其符號、ABI 或 31 項 UND。

原 wrapper 以 entry `a0` 為目的地址、`a2` 為來源地址，不使用 entry `a1`；程式固定對齊 256 bytes，按原順序解鎖、處理頁面、逐次載入與寫入 64 個 word、上鎖、以參數 1 呼叫 `19764` 的 SysTick-like 輪詢，再普通返回 0。這個 0 沒有驗證控制器成功。未加入另一版模型的 CSR 中斷遮罩或 Flash status=49 寫入。

所有 MMIO、RAM byte、來源 word 與目的 word 都經顯式合成 provider；沒有把數值地址轉為 host 指標、操作硬體或執行 RV32。`HALT` / `TRANSFER` 保留當時已發生的部分效果，未完成時不產生已知返回值。狀態位未知、GP 或計時 scale 未知會停在證據邊界。輪詢預算是 host 防止測試卡住的限制；原始輪詢沒有軟體上限。逐 word 讀取保留 alias 與 32-bit 地址回繞的語義，未假設 unaligned load 成功。

可執行：

```powershell
.\verify.ps1
.\verify.ps1 -Cpp
```

預設查找 `re-tsl9` 的 ID2966 韌體；也可傳入 `-Firmware <絕對路徑>`。腳本先核原檔及六段原始 bytes，編譯有 `/W4 /WX` 的 MSVC C11 / C++17 host 測試，再產生含來源與 executable 雜湊的獨立 build 收據。既有較舊 `tsl9-contract-model/flash_page.c` 使用另一個 Runtime payload，保持原樣。

測試涵蓋正常操作順序、entry a1 不影響行為、每個正常操作點的 HALT / TRANSFER 前綴、未知狀態與 GP/scale、輪詢預算、未對齊來源的 provider transfer、部分已知 word 及地址回繞。C/C++ 各 4 組、60,774 項檢查；這些都是合成契約測試，不能證明實體持久化、時序、中斷排除或 OTA。SDK 候選與原 record 支持 BLE 配對/非揮發儲存 hook 的推論；原 resident 的實際呼叫方式仍缺證，不能把此 wrapper 宣稱為 OTA 入口。
