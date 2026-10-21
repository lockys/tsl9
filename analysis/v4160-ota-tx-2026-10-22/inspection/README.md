# OTA 傳送函式的靜態輸入核對

[English](readme.en.md)

本目錄核對官方 ID2966 V4.1.60 中 `0x8A56..0x8B6E` 的 280 bytes。原始映像的映射起點為 `0x8000`，因此檔案範圍是 `0xA56..0xB6E`。`inspect.py` 實際比對官方 BIN、前一輪完整映像 ELF 與部分連結物件中的同一段 bytes，沒有執行任何韌體指令。

`inspection.json` 記錄輸入雜湊、原始 owner、符號及 RELA；`tx-llvm-disassembly.txt` 是固定雜湊 LLVM 工具對完整 owner section 的靜態反組譯。使用 section 範圍避免僅選入口符號時，在下一個區域符號處提早停止。

本次實測有 9 個外部直接引用、10 個內部引用及 11 個 owner 內 RELA。這些是現有物件記錄的範圍，不能排除未記錄的間接呼叫。符號名稱為重建專案的錨點，並非原廠符號。

`rea-session.json` 另保存本次實際連線狀態：REA 6.4.0 可回應，但未開啟原生目標；所需原生 provider 未配置，韌體區域分析 provider 在本環境不可用。因此這份反組譯來自獨立 LLVM 工具，不宣稱是 REA 的函式分析結果，也沒有為此安裝額外引擎。

函式語義與 C/C++ 的核對請見相鄰的 `source-review`、`implementation` 與 `ABI-review`。ROM 服務實作、實體 SRAM、晶片型號、藍牙傳輸與可燒錄性均未由這份靜態紀錄證明。
