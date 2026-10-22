# 候選 ROM 記憶體 leaf 的 C/C++ 重建

[English](readme.en.md)

本輪把三個候選記憶體 leaf 寫成可讀 C11／C++17：比較固定 byte、填值、向前逐 byte 複製。包含原本在參數判斷前執行的 MMIO 保存、清零、FENCE.I 及正常退出時恢復；以明示的 typed IO port 表達，而不是直接接觸硬體。**這些是條件式候選的演算法元件，尚不能替換原機 ROM。沒有新 BIN，現有 550-byte OTA 實驗與既有實驗映像不變。**

[C/C++ 程式與重現入口](../../experiments/tsl9-resident-memory-leaves/README.md) | [實際編譯及測試](implementation/README.md) | [獨立模型審查](model-review/README.md)

## 三者的語義差異

| 候選 RAM 位址 | 完整參考函式 | 已核對的正常行為 |
| --- | --- | --- |
| 0x200004BC | 62 bytes／19 指令 | 每次新鮮讀取 byte，與完整 32-bit A1 比較；全數相等才回傳 1。null 或長度零為 0。 |
| 0x2000039C | 46 bytes／14 指令 | 只寫 value 的低 8 bits，回傳前移後的目的位址；null／零長度不進入 byte 迴圈。 |
| 0x20000332 | 58 bytes／18 指令 | 每次先讀 source、再寫 destination，回傳原目的位址；重疊範圍仍向前複製，可能讀到自己先前的寫入。 |

以上三者在 null／零長度時仍有 MMIO guard 效果，不能直接等同標準 libc。讀寫失敗或無法返回時，模型只保留已發生的 prefix，不捏造正常 cleanup／成功回傳。

## 初始化設定的來源與下一個邊界

[MAC 檢查](precopy-review/README.md) 確認原始 caller 傳入 config+24、255、6；六 bytes 全 FF 會走拒絕分支。此完整 leaf 沒有 nested call、明示 S1／SP／S／GP／RA 改寫或設定寫入。結合先前填值與 copy 證據，在指定映射、有效記憶體、正常存取、無不利 alias／非同步變更等前提下，可把 App `staCB` 零值推導延伸至初始化的設定 copy；不等於已證明原機值。

[初始化後半段](continuation-review/README.md) 另外讀取兩份完整 228-byte／92 指令函式。複製後八個預設值 store 均避開配置 +52..55，第一個後續間接 call 則使用配置 +44。原 App 對應的 callback 數值來源為 **0x197F0**；tsCB／temperature 名稱仍是 header 順序推論。其 ADC／MMIO／其他呼叫仍待分析；初始化稍後還有另一個 direct call。不能宣稱 `staCB` 在完整初始化或執行期間永久為零。

## 驗證範圍

metadata 預設與實檔讀取分開；各範圍的 README、ledger 與 receipt 說明輸入、工具與實際結果。自有 HOST 測試每語言 27 案例／219 檢查，獨立測試每語言 16 情境／940 斷言，兩組各拒絕三個實際編譯的語義錯誤。這些只執行新寫的 C/C++ 與合成 IO 資料。

原生 C／C++ 的 compare、fill、copy 分別為 146／138／160 bytes，另有真實 local C begin helper 86 bytes，共 530 bytes／218 指令；原候選三個 leaf 合計 166 bytes／51 指令且沒有 frame。新元件有 context／結構回傳 ABI，不能因演算法測試通過而作為原位替換。原生編譯只產生物件與 IR，不執行 RV32。此處 530 bytes 與既有 OTA handler 的大小無關。

原生物件保留真實未解析 IO 符號；沒有數值假 provider、link、BIN、BLE／UART／CAN／Flash 操作或廠商服務呼叫。固定 Windows LLVM 的結果不代表其他平台的 native 工具已驗證。Python／POSIX shell 入口可攜，未新增 PowerShell 腳本。

原板型與已安裝 ROM／BOOT、原始完整暫存器／stack／IRQ ABI、MMIO 實際效果、Flash／NV 所有權及 OTA 接受／失敗恢復仍待證明。值得新增的離線設定診斷可顯示 MAC 是否全 FF、啟用 SNV 時 read/write callback 是否成對，以及零值欄位將套用哪些預設值；它可加入更新前的 ROM／NV 條件摘要，並區分條件推導與實測資訊。此診斷仍是提案，未加入原機功能，也不能決定映像可刷寫。
