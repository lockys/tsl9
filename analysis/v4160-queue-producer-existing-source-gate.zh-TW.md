# v4.1.60 佇列 producer：既有來源與驗證界線

## 規劃結果

`0x12bc8` 已有 `src/native/receive/ring_insert.c` 的 C 與 inline assembly 混合重建，不能把最近的獨立 C 語意候選算成新增覆蓋。上游 `0x16a7c` 的長度與旗標檢查不是 producer 本身的通用前置條件：producer 掃描 32 個、每格 12 bytes 的記錄，選首個起始 halfword 為零的格子；滿時不插入。

正式來源在 provider 呼叫前保存 ID 的低 16 位及長度低 8 位；呼叫時轉交完整長度，provider 指標從 `0x4004c` 重新載入。後續標籤寫入使用呼叫後實際 S0/S1，因此不能在 provider 未知時假設其必定保留。候選的兩次 byte 寫入也不能直接取代原 halfword 寫入並聲稱原子性等同。

## 本機既有收據重播

在本機以 `experiments/tsl9-ring-insert/verify.py --replay` 分別重播既有 C 與 C++ 收據：各 PASS，92 bytes、32 instructions、40 個負向控制，nominal linked code 與原始區段相同。收據 SHA-256 分別為 `c61f793250cb0c51fce0cc1756300fc5dec58274261827f24dbd0734d3161115`、`451182a600184814316a8cc728753a3d3144ebdec0e0b2679779bddfde2fdb3f`。重播檢查既有產物及收據，不是本次重新編譯或乾淨 checkout 證明；兩份均明示 `firmware_ready: false`。

元件 verifier 檢查物件的 82 個非控制位元組、三個 relocation、原位連結後完整 92 bytes 及限定 IR，並非實機執行。來源更動亦受來源 hash、IR 與原位布局 gate 限制。後續如試以 C 取代單一 load/store，應保留原始來源，另立候選並分別驗證 C/C++ 原位指令、暫存器、relocation 及 IR；不應僅憑較少 assembly 或合成 provider 測試宣稱整合完成。

以上不證 provider 的身分或 ABI、硬體執行、中斷安全、完整映像及可刷寫性。
