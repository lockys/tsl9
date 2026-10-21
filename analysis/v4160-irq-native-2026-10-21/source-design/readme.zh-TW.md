# 分支內部生命週期設計

原始 30-byte helper 先檢查完整 A1，再建立基底與讀取 MMIO。啟用時 A4=基底、A5=此次舊值，A0 原地更新；停用時 A5=基底、A4=此次舊值，A0 反相後更新。演算法僅需 A0/A4/A5，保留完整 A1 及 A2/A3/RA/SP；這不等於已證明編譯器能輸出該配置。

目前 C 的最佳化 IR 卻先讀取、同時計算 OR 與 AND_NOT、select、寫回，最後才依分支提交暫存器。`%3` 舊值、`%5` OR、`%7` AND、`%8` select 都留下生命週期；input-only 提交後再回傳還增加另一條需求。先前 value-returning bridge 雖消除最後一項，仍保留相同 select 結構。實際三／四暫存器 profile 的五個函式皆因 `Stack pointer required, but has been reserved.` 失敗。生命週期是有證據的解釋假說，尚非完整 allocator 根因證明。

`proposal.c.txt` 提出明確修改：各分支內各自進行即時讀取、運算、寫回及直接回傳 A0 bridge；`address` 改為 `offset`。另加入分支專用 A4／A5 基底。parent 修訂為直接 `lui`、僅輸出的 primitive，產生不同且依賴分支的 opaque SSA，避免共同讀取／select，也不再有空白 identity 的共享常數輸入 SSA。基底仍是 `0x40021000`，不能錯用含 offset 的完整位址。動態 helper mask 使用 A0 `+r` identity；main 每次使用立即數 `li` 的 A0 輸出，避免快取重複 C mask，且必須以 immediate constraint 要求編譯常數。分支、算術與記憶體操作仍是 typed C；Host identity 不增加 I/O 事件。

bridge 必須回傳綁定的 A0，呼叫端直接回傳此值，保留 A1 完整位元及各分支 A4/A5 順序，不能將 A1 轉成單純 0/1。main 仍依已證明順序保留六次新讀取 RMW、六次後續寫入及 CSR clear/set；最後直接以 bridge 回傳 A0=result、A1=0、A4=128、A5=`0xE000E000`，不要再保留舊 SSA 作第二次回傳。不得放寬 A2/A3/RA/SP 限制。

另一 worker 的單次允許 SP 診斷指出 helper 將舊值、兩個分支結果及 select 結果 spill；main 會快取重複 mask。它還發現 machine outliner 使用 T0，儘管 profile 宣告固定暫存器。這份診斷不構成候選，本審查未重跑；由 parent 另綁最終 receipt。若本機 compiler 文件確認旗標，明確停用這個已觀察到的 outliner 是有依據的單一修正，仍須檢查輸出 symbol／call／T0。parent 的四暫存器 A0/A1/A4/A5 配置必須證明每條 helper 路徑完整保留 A1，僅目的暫存器集合不足。這裡沒有編譯提案、搜尋 profile 或修改 model。

接受前須先通過 Host C/C++ 完整 trace／殘留值與實際編譯負向測試，再檢查原生 IR 與所有輸出函式，包括 outlined 函式、呼叫及返回續行。核對 helper 一次新讀取／正確寫回、分支輸出、完整 A1、每條指令目的暫存器、無 SP/frame/RA/T0 或隱藏 call、保留 A2/A3，以及 main 二十個有序效果與最終輸出。opaque 基底只能使用明確限定的 identity 證明；若仍 spill／outline，應記錄失敗，不能放寬契約。大小必須重新量測。一般返回契約不能證明暫態暫存器、stack、非同步 IRQ、原址配置、ROM、OTA 或硬體相容。

`verification.json` 保存來源雜湊與觀察。此設計審查僅讀取既有檔案；沒有編譯、執行、網路、硬體或產生 BIN。
