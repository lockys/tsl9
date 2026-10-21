# 時脈暫存器重建審查

本審查與不可修改的相鄰 `caller-review` 分開。來源是原始 ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 及已封存的 214 位元組、69 條時脈指令證據。呼叫端審查已確認，query 依路徑產生的 A3 不能只保留入口值：此原始輸出經已知正常初始化前綴，到達 `0x131E0` 的未知間接 callback。

審查產品為新的可讀元件 `experiments/tsl9-v4160-clock-registers/src/`，不是先前僅重建記憶體效果的元件，也不是 ISA interpreter。主機暫存器 commitment 只觀察新 C hook 的參數，無法單獨證明原生實體暫存器賦值。Native write-set、堆疊、函式大小、編譯器 reservation 仍需另以實際編譯結果證明；任何主機測試都不證明實機中斷 ABI、硬體或 OTA 行為。

## 獨立測試設計

獨立 harness 重用 `apk-analysis/tsl9-v4160-native-clock-2026-10-21/code-review/test_independent.c` 已封存的**獨立**記憶體 fixture，沒有包含父層測試實作。此 fixture 核對全部 selector、倍率欄位、新 config/global 讀取、四／三個 live GP 使用點及數值位址環繞、每個 table index、shift byte 與 unsigned quotient 邊界。

新增預期值分別推導每條路徑的原始 A3；外部 source 分支須在第四次新 config sample 後，立即設定 A2=`0x00C00000`，其他路徑不得寫 A2。Query 最終 A4 必須保留完整 unsigned byte，A5 必須是新 word 右移後的完整值。派生 A4 必須為 1000，A5 必須保留已遮罩 quotient 乘以 1000 的完整乘積，不能因記憶體 store 為 16 位元就將 A5 一併截斷。每個輸出 commitment 都須位於最後一個原始記憶體效果後，且不能提交另一個函式的輸出。

已在實作等待 freeze 時審查父層測試：它擴充先前記憶體 fixture，加入各分支 A3、條件式 A2 時點／數值、query A4/A5 與派生完整 A5。此項屬測試覆蓋率審查，並非已編譯測試結果或原生 ABI 證明。

## Freeze 後的主機驗證

父層 freeze 四個 C／標頭後，獨立 C11、C++17 各通過 **4 組、5,345 個案例、250,316 次檢查**。其中 214,811 次來自先前獨立記憶體 fixture，新增檢查觀察來源推導的正常返回暫存器 commitment 與條件式 A2 hook。Freeze 版本未發現阻擋性的來源差異；external mask 僅在外部分支產生，派生乘數保留為 1000，同時用於乘積與最終 A4。

每種語言另實際編譯、執行八個錯誤產品版本：錯誤預設 A3、內部 A3 誤設 18 而非 17、錯誤外部遮罩相等 A3、先保留正確頻率選擇再將 fallback A3 左移 13、無條件寫 A2、A4 輸出只留 shift 遮罩而非完整 byte、交換派生 A4/A5、派生 A5 截成 16 位元。合計 **16 個實際已編譯版本**均被獨立執行期 assertion 拒絕。大多數變異仍保持正確記憶體效果，因此只測記憶體不足以證明暫存器契約。編譯失敗不算行為拒絕。

可用 `audit.py --language both` 重現主機審查。Receipt 綁定四個實際來源／標頭、獨立 wrapper 與不可修改的 fixture、所需標頭、共用編譯 helper、舊來源與呼叫端證據、編譯器、實際執行檔及編譯日誌；每次執行期間所有輸入 hash 均未變。本證據限於主機 hook 的值與順序，實際原生 commitment、暫存器 write-set、配置位置、堆疊／中斷與硬體相容仍是獨立檢查。

父層最終 C／C++ receipt 各通過 6 組、293,845 次檢查，重播既有 214 位元組／69 條指令／50 個負例的來源證據，並綁定新解碼的原始 destination 事實：query 只寫 x12–x15，共 44 條 destination 指令；fields 只寫 x14–x15，共 8 條。返回公式仍屬靜態來源審查，不是 ISA 執行證明。`check-review.py` 將這兩份父層正式 receipt 與兩份獨立 receipt，對照目前輸入、實際編譯器與執行檔 digest；同時由正式 receipt 綁定最終父層 runner、source map、分語言文件，核對過程不執行任何程式。
