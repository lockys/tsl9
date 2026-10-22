# 事件 callback 的 C/C++ 重建

[English](readme.en.md)

本輪研究官方 ID2966 V4.1.60 的 `0x8614..0x888C`：632 bytes、217 條原始指令，含二十六個直接控制參照、六十四個記憶體操作與十五個不透明間接呼叫。來源解析、可讀 C/C++、合成主機行為與原生配置證據分開保存。**這個 callback 尚未納入完整映像，沒有新增 BIN，也尚未證明可刷寫。**

## 已重建的邏輯

事件的 LOW16 bit15 優先，其次是 mask `0x8`；其餘路徑先比對兩組 context byte，再依 mask `0x1/0x2/0x4` 分派。context 與事件值保留完整 32 bits，不能套用候選 SDK 的窄參數型別。兩組記錄的緩衝區步距是 1062 bytes，傳送描述欄位、已處理長度及重試次數保留原始 halfword／byte 寬度與 fresh read。

mask `0x1` 與 `0x2` 路徑對同一候選 ROM gate 的判斷不同：前者要求回傳值恰好等於 1，後者只檢查最低位元。分段長度使用截成 16-bit 後的有號剩餘量及另一個不透明呼叫的回傳值；失敗路徑與成功後更新長度／提交事件的路徑分開重建。未知 ROM 仍以數值 slot、實際設定的引數與回傳邊界表示，沒有宣稱已識別原機 SDK。

[初始化來源](entry-plan/README.md)另核對三次將 `0x8614` 傳給間接呼叫的指令，以及回傳 byte 被存入 GP_after+`0x9D/0x94/0x98` 的位置。S0、S1 與 GP 在不透明呼叫後是否保存仍待證；候選 absolute slot 與預設 connection halfword 值均保留條件。

## 證據與未解決差距

- [來源審查](source-review/README.md)直接重讀原始 BIN，驗完整指令與角色；來源運算元反例不靠檔案雜湊拒絕。
- [實作](implementation/README.md)保存實際 C11／C++17 HOST 與原生編譯證據。HOST 的 named values、引數 projection 與合成 frame 是演算法測試介面，不是 ISA 模型或原機實體 GPR-prefix 證明。
- [獨立審查](ABI-review/README.md)使用獨立合成案例並讀取真正原生 ELF／IR。間接呼叫後未明示設定的 scratch residue、實體 SP／GP／暫存器保存、返回地址及異步行為仍須獨立處理。

原生 probe 沒有取得原址適用性；不得因嚴格連結成功或 HOST 測試通過，就把它放回 632-byte 原區域。原機 ROM／BOOT 身分、晶片、Flash 別名、CRC／簽章與 BLE OTA／失敗復原也仍未證實。原始 BIN 只作資料讀取，未執行或模擬 RV32，未連接硬體或呼叫廠商 API。

修正後 baseline 需 944-byte 主函式與 90-byte 呼叫 primitive；只將該 primitive 明確內聯，可降為單函式 658 bytes、48-byte frame 及十五個間接呼叫。仍超出原區域 26 bytes，且有額外 S10 保存、儲存順序、返回位址及不透明 callee 可觀察的暫存器差異。這是實際原生改善，並未因此通過完整 ABI 或整合閘門。

目前完整實驗映像仍是[上一輪 TX 整合版本](../v4160-tx-image-integration-2026-10-22/README.md)，保留原始 callback 承載。後續應先縮小原生差距、整理實際呼叫邊界與進入／返回契約，再審查新的完整映像整合。更新等待原因的來源位置已補入初始化分析，仍是研究提案，沒有新增硬體功能。
