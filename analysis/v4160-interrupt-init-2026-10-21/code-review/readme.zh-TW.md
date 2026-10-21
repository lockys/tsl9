# 可讀初始化實作審查

本審查針對 `experiments/tsl9-v4160-interrupt-init/src/interrupt_init.c` 及其公開標頭。主機測試與 freestanding 版本共用相同邏輯，`TSL9_IRQ_HOST_TEST` 僅切換 MMIO、CSR 存取 primitive。獨立原始證據為不可修改的相鄰 `abi-review/final-audit.json`：ID2966 runtime SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，涵蓋 264 原始位元組、94 條指令。

目前未發現阻擋實作的來源差異。四個 helper 每次呼叫均重新讀取一次 32 位元值，以 `enabled` 是否非零選擇 OR 或 AND 補數，寫入一個 word 並回傳結果。`0x9A42` 入口重建六次 helper 呼叫、六次依序尾端寫入、CSR 的 `0x88` 清除與設定；回傳值保留原始 A0 所觀察到的最後一次新讀值及遮罩結果。實作沒有合併三次獨立的 `0xE000E104` store、快取設定與清除間的讀值、還原舊 CSR 快照、自創成功狀態或加入錯誤 cleanup。

主機 backend 僅記錄數值位址並操作一般記憶體。獨立 C harness 核對所有 helper 位址、包含高位元的零／非零 selector、使用個別新讀值的完整 20 筆效果 trace、最終回傳值，以及最後 set 前注入的即時 CSR 改變。測試使用確定性的多種位元資料，不執行原始 firmware。預期表由已封存的原始列推導，並未重用父層測試實作。

`audit.py --language both` 透過共用的可攜編譯器啟動流程，將同一份重建程式分別以 C11、C++17 編譯。每種語言也實際編譯三個刻意錯誤版本，再執行這些主機程式，要求 assertion 拒絕：使用快取而省略清除端讀取、還原入口 CSR、把一個 byte 寫入擴大為 word。編譯失敗不算行為負例通過。Receipt 記錄編譯器、實際執行檔、選項、日誌、來源輸入、原始證據封存及其 SHA-256；每次語言測試前後都核對父層 C/H、測試、驗證腳本與共用編譯 helper 未變。

獨立 C、C++ 各通過 4 組、34,267 次 assertion，合計六個已編譯行為負例都被拒絕。父層最終測試各通過 4 組、6,680 次 assertion，並執行 264 位元組、94 條指令的來源 gate、拒絕 94 個原始位元組變異。`check-review.py` 核對實際執行檔、編譯器 digest 與 receipt 閉包。C receipt 有一個明確記錄的上下文 pin 早於父層最終 `verify.py`；該腳本未被獨立 harness 編譯或呼叫。所有編譯使用的 C/H／測試與共用編譯 helper 均符合目前檔案。最終父層腳本由兩份正式父層 receipt 及獨立 C++ receipt 綁定，舊 C receipt 保持不變。

原生 primitive 使用符合寬度的 `volatile` 存取與附 compiler memory clobber 的 volatile CSR 組語。主機行為不能證明原生編譯器輸出相同操作，需另外審查原生編譯／IR。即使原生編譯通過，也不能證明原始 caller-saved 暫存器殘值、堆疊布局、指令時序、實機 CSR 意義、特權、中斷進出 ABI、實體 MMIO 作用或 OTA 相容。新公開符號是重建符號，尚未證明可取代原 firmware 位址。本審查沒有硬體存取、原始 RV32 執行、ISA 模擬或網路操作。
