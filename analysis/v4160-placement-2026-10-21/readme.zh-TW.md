# 原址配置與中斷暫存器契約

目標為 ID2966 V4.1.60，共 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。本輪只把原始韌體當資料讀取，不執行／模擬 RV32，也不存取硬體或廠商服務。

- [原始範圍與引用證據](source-review/readme.zh-TW.md) 綁定八段共 540 bytes、691-section／8,280-RELA carrier 及完整固定配置。IRQ `0x9A42` 本體是 144 bytes，四個 RCC helper 各 30 bytes，而且各有其他呼叫端。已納入程式碼未見外部直接跳入內部，但 939 條間接指令使計算式目標仍不能排除，不能據此任意利用看似空出的位元組。
- [ABI 反證](abi-review/readme.zh-TW.md) 確認舊版 118-byte 初始化與 22-byte helper 會改寫 A2／A3，並有不同的 A1／A4／A5 返回值，不能直接替換。原始 IRQ 後 A3 還會到未知 callback，不能僅依一般 C 呼叫慣例捨棄。
- [有限編譯探針](compiler-probe/readme.zh-TW.md) 保存實際 C／C++ `-Oz` 結果：reset leaf 66、fragment 68 bytes，先前為 78／80，原始為 62；時脈查詢／衍生欄位仍是 196／38 bytes。同 section 的 C.J 可以是兩 bytes；已驗證 no-relax 配置下，對外部符號寫 `c.j` 實際產生四-byte JAL x0。跳板幾何不證明區段可用或 ABI；196-byte 查詢放不進任一選定的原始連續範圍。
- [新 C/C++ 審查](code-review/readme.zh-TW.md) 檢查可讀的 interrupt-register 元件及 helper／初始化正常邊界契約。
- [新原生審查](compiler-review/readme.zh-TW.md) 分開記錄實際編譯、實體目的暫存器檢查、配置失敗與原址限制。

新程式位於 `experiments/tsl9-v4160-interrupt-registers/`。合成主機觀察涵蓋記憶體／CSR 與正常邊界輸出，不能證明實體暫存器或中斷途中狀態。成功或被拒絕的編譯配置以各自機器碼證據為準；總大小算術與數值 JAL 證據都不能證明可安全整合進原址。

交付選定的程式、文字與收據 metadata，歷史編譯封存留在工作區；目的地與 checkout 驗證建立新的本機產物。原始 BIN／APK 與先前完整映像 carrier 不變，未產生新韌體 BIN，也未進行實體 OTA 驗證。文件依語言分開，每個 `README.md` 只提供語言入口。

發佈 checkout 的新探針使用 `python3 analysis/v4160-placement-2026-10-21/run-probe.py reset --project-root . --tool-dir /path/to/llvm/bin --language both`，延續形式加 `--fragment`；其他探針把 `reset` 改成 `clock` 或 `thunk`。封存 producer 保留原工作區路徑常數，此 adapter 選取已存在的發佈／工作區依賴與確切韌體資料，只在記憶體中調整路徑常數，保留封存檔與雜湊檢查，並另存自身來源證據，不會補回未交付的歷史編譯封存。直接重播 `compiler-probe/check_probes.py` 仍需要原工作區路徑；發佈後的新編譯使用 adapter 入口。
