# 1316a host-only C harness

**本次沒有編譯或執行任何 C，也沒有使用 target、硬體或 simulator。** 此處是對已提交的 `../v4160-1316a-default-candidate/model.c` 之抽象事件模型所寫的 C99/C11 host 測試，不是對實機行為的驗證。`harness.c` 直接 include 該檔；記憶體為獨立稀疏 byte 表，未設值讀作零，word 按 little-endian 組合，位址以 uint32_t 回繞。

此稀疏表以所有未列位址的 byte 為零來**定義已初始化的抽象記憶體**，不是假設實機未初始化記憶體為零；讀寫均在此抽象環境中成功，word 讀取及 halfword store 均對齊，對應原模型的成功、對齊訪存與共享記憶體 domain。未建模的 stack 仍依原模型假設有效且不別名；這些 fixture 不證明實機的記憶體映射或可達性。`alias0` 的 gp=0x2000c248，對齊的 gp+84=0x2000c29c 讀取預設零 byte 和首個 halfword store，little-endian 得 0x0fff0000；`wrap` 的 gp=0xffffffac，gp+84 回繞為對齊的 0，初始化指標 0xfffffffc 再加 12 得 a0=8。

有限的固定字面事件 fixture 檢查所列案例的讀寫與呼叫順序、兩個 callback 回傳零（模型中代表不正常返回的邊界）、兩次 JALR 清除 bit 0、三個 gp+84 與 store 重疊位置、gp 與指標加法回繞、第一個 callback 修改後續指標與 slot、tail。若 `model_1316a` 返回，測試會檢查事件與次數；模型自身回傳型別為 void。非返回是 callback 透過介面回傳零的抽象表示，並非模擬實際無限執行；測試沒有逾時機制，不能保證遇到無限循環時結束。任一執行到的檢查失敗則程式非零退出。

只執行 Python 靜態檢查（從 repo 根目錄）：

```text
python -B experiments/v4160-1316a-c-harness/check.py
python -B -O experiments/v4160-1316a-c-harness/check.py
```

檢查固定映像及指定視窗、原 C 模型、harness 的 SHA-256，核對 C 字面 fixtures，並對各 pin 的資料變動及錯誤 mask、缺 tail、順序與 alias 進行負例。它不執行 C，也不證明 C 語法或實際測試結果。映像路徑固定為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`；缺檔或 pin 不符即失敗。Python 檢查不使用 assert，因此 `-O` 不會移除檢查。
