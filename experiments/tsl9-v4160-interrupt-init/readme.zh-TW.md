# 可讀的中斷初始化重建

此 C11／C++17 實作重建 ID2966 V4.1.60 入口 `0x9A42` 及四個 RCC 輔助函式的有序周邊存取與 A0 結果。原生編譯使用 volatile word／byte MMIO 及兩條 CSR 指令；不是把原指令擷取陣列當成可讀 C，也不包含通用韌體直譯器。

來源證據涵蓋五個完整函式，共 264 bytes／94 條指令。原入口先清除 CSR `0x800` 的 `0x88` 位元，執行六次重新讀取的 RCC 讀取／修改／寫入，再依序寫入三個 priority 類 byte 及三個 enable 類 word，最後設定 CSR 的 `0x88` 位元。最後設定不附條件，也不是還原入口值。回傳值是最後重新讀取 `0x4002100C` 後與 `~0x101D` 相與的結果，沒有自行增添成功狀態。

```sh
sh experiments/tsl9-v4160-interrupt-init/verify.sh --language both
```

需要 Python 3.10 以上及 C11／C++17 編譯器，也可直接呼叫 Python 入口。驗證先核對確切原始 BIN、封存來源成員及 94 個原始指令負例，再編譯自行重建的主機測試。測試只用行程內合成 MMIO／CSR 紀錄替換存取原語，不接觸實體裝置。兩語各通過 4 組／6,680 項，涵蓋讀取之間值改變、所有非零 helper 旗標，以及原先未設定的 CSR 位元。

原生編譯與靜態產物檢查另位於 `analysis/v4160-interrupt-init-2026-10-21/native-plan/`。RV32 元件不等於韌體映像，也未證明能替換原始位址的實作。一般 C 不保證原 caller-saved 暫存器殘值、確切堆疊槽、指令時序、fault 行為或中斷 ABI；本項只重建一般呼叫及外部效果介面。既有完整映像 gate 及缺少實作的 resident 入口均保留，目前沒有驗證可供 BLE OTA 使用的重建 BIN。

根目錄跨平台 registry 仍涵蓋原先四個模型，本元件請用上述獨立指令。shell、本機 Python 與跨平台 CI 證據分開報告。上一輪 GitHub CI 因帳戶付款／支出限制而未能啟動。
