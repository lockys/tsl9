# OTA 命令本體的實作範圍

目標是把原始 `0x9C4A..0x9E5C` 的 530 bytes 從原始承載提升為共享 HOST／native 的可讀 C/C++。官方 ID2966 映像 SHA-256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；本體切片是 `693eba9e21b786525b457b538d998a997a601ee46327621a2302ede1b2f274c5`。既有完整映像中的此範圍仍是原始指令，不可把既有高階 HOST 模型計成已整合 native C。

## 必須保留的行為

- U：先清 active，再比較 UID；UID 長度是 `(length-1)&255`。mode 1 才排兩個切換 callback，最後才回覆。
- S：回覆第一個 byte 使用比較 UID 前保存的 mode；成功比較後重新讀 live mode，決定 active。回覆第二個 byte 是 capability 1。
- W：先 active，再長度 1026，再 BE16 頁號及原範圍條件。保留必要的對齊 copy、四次 256-byte primitive，以及逐 word「先 Flash、後 live RAM」的讀回順序。不將讀回比對改稱 CRC／簽章。
- R：active、精確長度 16、UID14，才讀 BE16 頁號及要求頁面回覆；不增加 W 的頁碼上限。
- E：active、精確長度 15、mode 0、UID14，通過後才清 active、排程與空回覆。
- 原始 `0x9DF4` 是會設定 RA 的 `C.JAL`，不可再誤當無連結尾跳。停止／轉移後不得繼續下一個效果，也不回滾已發生的寫入或排程。

這段 W 流程寫入 BOOT 數值別名 `0x08001000 + page*1024`，不是已證明可用來將新 Runtime 刷入自己的流程。

## 程式與驗證安排

共享高階 C 保留原分支與數值運算；窄 ports 分別實作 HOST 合成 provider 與 native volatile memory／明示 opaque call。HOST 未知輸入與 callee 效果必須可停止；不以零或固定成功值補未知。原始重要實體暫存器與 caller 前綴仍是額外的 ABI 義務，不將 named C state 當作實體暫存器已相同。

先實際編譯 C11／C++17 的 ET_REL、LLVM IR、完整 MD 與 disassembly，再量測真實函式與外部重定位。缺少 callee／callback provider 時保留真 UND；不以 ABS、數值供應者、stub、偽造 FUNC 大小或原 BIN 指令補齊。能否連結或取代原 raw owner，須以實際來源、provider、CFG／來向與版面證據決定。超出範圍就記錄差距，不以 padding 或旗標搜尋假造可整合結果。

實作與獨立 HOST fixture 聚焦命令條件、效果順序、live 重讀與少數停止邊界，不重跑舊 427,249 檢查矩陣。新測試只執行經 machine guard 驗證的本機 HOST 程式。原始指令欄位與新原生物件由不同 scope 審查；不執行或模擬 RISC-V，也不連接硬體或廠商服務。

MCU／ISA、實際 resident／BOOT、RAM／GP／stack／IRQ、Flash／更新接受與失敗復原仍待證。這個實作範圍不是完成整體目標的替代定義；未通過這些條件前，不宣稱有可刷寫的重建 BIN。
