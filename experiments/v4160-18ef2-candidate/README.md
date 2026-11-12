# 0x18ef2 非正式事件模型候選

此目錄只依 `../v4160-18ef2-store-loop-evidence/` 的正常入口靜態證據提出純 C 候選，並非正式或完整重建。來源映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；映射基址 `0x8000`，視窗 `[0x18ef2,0x18f56)` SHA-256 `8cd6ddd7edd2d5a0adb776d396c8cb499d64ce974f38df7e651f9af720114dd8`，逐 byte pin 見測試及原證據 `verify.py`。這是身分識別而非來源認證。

`candidate.c` 用 `read32`/`write32` 回呼表示每一筆 word 事件；依序做控制暫存器 RMW、兩次獨立 polling、64 次來源讀後目的寫及每次 polling、再次 RMW、polling、最後 RMW。回傳入口 a0 清低八位；地址相加以 uint32 包回。不用 memmove、不快取 polling、不設 timeout，也不固定控制暫存器其餘位元。若 polling 位元持續非零，沒有進度或返回保證。

C 候選的使用前提是呼叫期間 bus 物件、context 及其所需狀態保持有效，且每次取用的函數指標有效、符合宣告型別；回呼正常返回。非資料競爭的重入可以動態修改共享 bus，包括 context 和函數指標，後續取用依當時內容；不假定回呼純粹或 bus 不變。這些僅是 C 模型的使用前提與已描述行為，不保證真實匯流排、硬體、異常、並行者或任意非本地控制流的行為。C API 僅是事件抽象，**不證 ABI、inline asm 或編譯器 codegen**；C 未編譯或執行，也未執行或模擬 target。無證據保證位址有效、對齊、可存取或成功儲存。

`test_reference.py` 只執行 Python 符號表達式／事件參考模型，不載入或執行 C，也不覆蓋 C callback 重入；不是 target 模擬或 C 等價性證明。它以 SHA-256 pin C 原始檔並對記憶體中的單 byte 變異做負向測試；這只檢查檔案身分，不證明 C 行為，也不修改檔案。Bus 預設未設定字為零、寫入更新字典；可對任何地址排入有限的讀值，佇列耗盡退回字典，這只是測試環境，不是硬體假設。bounded bus 對四個 polling 入口各檢查指定的持續忙碌事件前綴，再以例外由測試觀察者明確中止；這不是模型 timeout 或返回，也不能單憑有限前綴證明無限執行。測試另覆蓋逐事件順序、變動的 polling 值、符號控制值、前向重疊、地址 wrap、來源／目的與 MMIO 數值別名；負向變異測試證明預先讀取所有來源會改變重疊行為。上輪已固定證明 `0x9c34` 的 JAL 指令指向 `0x18ef2`（位於 `0x9c0a` caller 場景），但不證明可達性或實際入參；此處測試參數純屬虛構。

從 repository 根目錄執行（不編譯 C）：

```text
python -B experiments/v4160-18ef2-candidate/test_reference.py
python -B -O experiments/v4160-18ef2-candidate/test_reference.py
```
