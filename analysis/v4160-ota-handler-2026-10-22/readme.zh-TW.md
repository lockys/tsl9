# OTA 命令本體：共享 C/C++ 與實際原生差距

[English](readme.en.md)

本輪新增原 `0x9C4A..0x9E5C` 的共享 HOST／native 可讀 C/C++，涵蓋 U／S／W／R／E 命令。原始本體為 530 bytes／169 條指令，當前完整映像仍保留原始承載；本輪元件尚未納入 BIN。

## 實際程式與驗證

- 新高階 C 與窄 ports 分開。HOST 使用明示數值記憶體及 callee provider；native 使用 volatile 讀寫、live GP 與明示呼叫橋接。原始 BIN 只作驗證輸入，沒有產生新指令的 byte 模板或缺碼 fallback。
- C11、C++17 實際 HOST 測試各通過十個案例／8,292 檢查與三個編譯語義反例；獨立 fixture 各通過十六個敘事、十八次 dispatch、898 項行為檢查與四個編譯語義反例。合成測試不等於硬體執行；HOST 程式先經不可變的 machine guard。
- C11／C++17 的真實 ET_REL 均為單一 **776-byte FUNC／285 條指令／112-byte frame**。原始為 530 bytes／48-byte frame；新元件多 246 bytes。完整 MD 包含三份專案來源及一份 Clang resource header。
- 物件有九個真 UND：六個直接 callee、三個 callback 位址。23 筆重定位為十五個 JAL 與四組 callback HI／LO；另有一個由 slot `0x4004C` 讀取的間接呼叫。W quarter 在原碼只有一個迴圈 callsite，native 展開後有四個；不能用靜態 callsite 數量相同替代語義核對。
- 獨立審查讀取實際 object／IR／MD／工具與來源身分、全部 285 個指令運算元及三個原生反例。**沒有執行 RV32、連結新 ELF、產生新 BIN 或操作硬體。**

程式位於 [model](../../experiments/tsl9-v4160-ota-handler/README.md)。來源與測試證據見 [implementation](implementation/README.md)、[原始來源與 consumer 核對](source-review/README.md)、[獨立 HOST／native 審查](ABI-review/README.md)。[實作計畫](plan.zh-TW.md)與[整體範圍／缺口盤點](status.zh-TW.md)分別說明此元件與完整目標。

## 重要行為

W 保留 active→長度1026→BE16頁碼與範圍→必要對齊 copy→四次256-byte primitive→逐 word「先 Flash、後 live RAM」讀回→回覆的順序。它寫的是 BOOT 數值別名 `0x08001000 + page*1024`，不是已證明可將 Runtime 刷入自己的流程。

U 先清 active 再比較 UID，UID 長度仍為 `(length-1)&255`。S 將比較前的 mode 存入回覆，再依比較後的 live mode／GP／S1 決定 active。E 保留 active、strict15、mode0、UID14 的順序；R 保留 strict16、UID14，沒有自行加入 W 的頁碼上限。HALT／TRANSFER／UNKNOWN 會停止後續效果，不回滾先前效果。

來源審查另修正新 C 的 W 回覆邊界：A3 是最後一次 source word、A4 是1024、A5 是失敗 offset 或成功1024。這些是原碼可見的具體投影，不是宣稱所有中間／ambient physical registers 相同。`0x9DF4` 是設定 `RA=0x9DF6` 的 `C.JAL` 至 `0x9B8E`，不是 tail jump。

## 尚未整合的原因

新物件比原530B範圍大246B；缺少經審查的新位置、存活來向、continuation 與完整映像版面方案。九個 UND 可以在後續以現有真實 section-backed providers 處理（[基線 inventory](existing-providers.json)），但它們目前沒有被連結，不能用數值 ABS、stub 或偽造 FUNC 大小補上。

HOST named S／SP／GP 是明示的來源值與效果模型，不是 CPU 模擬器；native 仍以一般 callee preservation 為條件。native 的兩-byte C 回覆陣列不等於原始 live SP+12；完整 scratch／S／SP／RA／alias／非同步契約仍未證明。這不是因函式較長就宣告 ABI 失敗，也不能只因編譯成功就准入原硬體。

原完整 TX 實驗映像 SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` 維持不變。完整目標仍包含原 MCU／ISA、installed ROM／BOOT、RAM／IRQ、Flash、BLE OTA 接受與復原；**尚無驗證可刷寫的重建 BIN**。離線封包預檢與等待原因顯示仍是提案，未當成硬體功能交付。

## 重跑

```sh
python3 -B experiments/tsl9-v4160-ota-handler/verify_host.py --project-root /absolute/re-tsl9 --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler/build/new-host
python3 -B analysis/v4160-ota-handler-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler/build/new-native
```

輸出目錄只可新建；replay 以實際 `verification.json` 為輸入。獨立 review 與 metadata／actual flags 見各子目錄。此輪實際環境為 Windows；Python／shell 介面本身不代表 Linux／macOS 已驗證。
