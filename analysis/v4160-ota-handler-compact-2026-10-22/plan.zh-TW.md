# OTA 處理器體積縮減與 callee 契約計畫

[English](plan.en.md)

完整目標仍為原硬體可使用原藍牙 OTA 更新的重建 BIN。這輪處理的是先前 776-byte 共享 C/C++ 元件的實際體積與必要 callee；不得把元件測試當成實機相容證據。

1. 以既有已封存 C/C++、真實 ET_REL、LLVM IR、原始 530-byte 指令及完整映像作基線。先重讀真實重定位與迴圈，記錄前輪三份 README 的靜態 callsite 誤述。
2. 只根據具體 compiler IR／來源假設做有界變更。先確認停用展開是否有效；若無效，保留否定證據。分離 native 回覆陣列與參數物件的生命週期時，保留八個暫存器 I/O、memory clobber、volatile 操作、所有 HOST 效果與 W 回覆投影。
3. 原碼的三組 terminal 回覆共用位置可作第二個具體 C 控制流假設；共用標籤仍須保留每條路徑的參數 mask、來源位置、呼叫順序與停止行為。不得為縮小而刪除未知 callee 所可能觀察的參數。
4. 原始 UID 比對、builder 及 slot `0x4004C` 的實際運算元與呼叫鏈由獨立 scope 追查。候選 ROM 函式只能形成有條件結論，不代表已安裝 ROM。
5. 以本組與獨立 fixture 重新驗證實際 C11／C++17 HOST，再獨立讀取真正 native ELF／IR／MD／完整指令及工具與來源身分。舊 seal 與舊 pass 不修改。
6. 將驗證後的來源交付 `re-tsl9`，在交付及發布副本重跑，保護所有既有檔案與映像；於已授權私有 GitHub 提交里程碑。

限制仍包含原始 physical S／SP／GP／RA、scratch／alias、非同步觀察、installed ROM／BOOT、實機 Flash、OTA 格式／接受／復原。大小符合並不自動證明任何一項限制；此輪未安排新 BIN、連結、RV32 執行／模擬、硬體或供應商 API。
